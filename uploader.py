import os
from ftplib import FTP, error_perm, all_errors

# url, kullanıcı e-postası, şifre
ftp_data = "", "", ""

if not len(list(filter(lambda d: bool(len(d.strip())), ftp_data))):
    print("FTP bilgilerini dosyadan kayıt edin!")
    exit()
ftp = FTP(*ftp_data)

def placeFiles(ftp, path):
    for name in os.listdir(path):
        localpath = os.path.join(path, name)
        ftppath = name
        if os.path.isfile(localpath):
            print("STOR", ftppath, localpath)
            ftp.storbinary('STOR ' + ftppath, open(localpath,'rb'))
        elif os.path.isdir(localpath):
            print("MKD", ftppath)

            try:
                ftp.mkd(ftppath)

            except error_perm as e:
                if not e.args[0].startswith('550'): 
                    raise

            print("CWD", name)
            ftp.cwd(name)
            placeFiles(ftp, localpath)           
            print("CWD", "..")
            ftp.cwd("..")
            
def deleteAll(ftp, path = ""):
    wd = ftp.pwd()
    names = ftp.nlst(path)

    for name in names:
        if os.path.split(name)[1] in ('.', '..'): continue

        try:
            ftp.cwd(name)
            ftp.cwd(wd)
            print("CWD", name)
            print("CWD", wd)
            deleteAll(ftp, name)
        except all_errors:
            print("DELETE", name)
            ftp.delete(name)

folder = input("Yüklenecek klasör: ").strip()
while True:
    ftp_folder = input("cPanel'deki klasörün konumu (Boş bırakırsanız FTP hangi klasöre bağlıysa o klasörü seçer): ").strip()
    if not len(ftp_folder):
        ftp_folder = None
        warn = input("UYARI! FTP, cPanel'in ana klasörüne bağlıysa çalışmayabilir ve verileriniz güven altında olmaz. Eğer klasör yolunu değiştirecekseniz onaylayın. y/N ").strip()
        if warn.lower() == "y":
            continue
    break
delete = input("Önceki dosyalar ve klasörler silinsin mi? Y/n ")
if not delete.lower() == "n":
    deleteAll(ftp, ftp_folder)
    input("Önceki dosyalar ve klasörler silindi! Devam etmek için enter tuşuna basın.")

print("Klasör belirtilen konuma yükleniyor...")
if ftp_folder:
    print("CWD", ftp_folder)
    ftp.cwd(ftp_folder)
placeFiles(ftp, folder)

print("Dosyalar yüklendi!")
ftp.quit()
