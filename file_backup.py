import warnings, os, zipfile, pysftp, time
warnings.filterwarnings("ignore")

mypath = '/Users/bestin/Documents/'
dir_name = 'sftp-backup'

os.chdir(mypath)

# Sort files by creation/modified date
def sorted_ls(path, order = 'ctime'):

    if order == 'mtime': mtime = lambda f: os.stat(os.path.join(path, f)).st_mtime
    elif order == 'ctime': mtime = lambda f: os.stat(os.path.join(path, f)).st_ctime

    return list(sorted(os.listdir(path), key=mtime))


# Sort files by timestamp and delete files older than a specified limit
def filter_files_on_limit(files_unsorted, limit):
    sorted_files = []
    removed_files = []
    files_to_be_removed = []

    for file in files_unsorted:
        if file.startswith("backup_"):
            prefix_file = file[7:-4]    # Split string between 'bakup' and '.zip'
            sorted_files.append(int(prefix_file)) # Appending epoch timestamp of each file after casting to int

    sorted_files.sort(reverse=True)  # Sort list of integer epoch timestamp values
    while len(sorted_files) > limit :
        removed_files.append(sorted_files.pop())  # Pop items from sorted list to another list if number of items in list > limit (3 for local, 20 for remote)

    for items in removed_files :
        files_to_be_removed.append('backup_'+str(items)+'.zip') # Generate files name for popped out list

    return files_to_be_removed


##  Delete files on local machine
def delete_files(rm_files_list):
    print("********* Deleting local files *********")
    for file in rm_files_list :
        print(mypath+file)
        os.remove(mypath+file)

# Refer https://stackoverflow.com/questions/1855095/how-to-create-a-zip-archive-of-a-directory

    # Zip a directory
def Zip(output_filename):
    def zipdir(path, ziph):
        # ziph is zipfile handle
        for file in os.listdir(path):
            ziph.write(os.path.join(path,file))

    zipf = zipfile.ZipFile(output_filename, 'w', zipfile.ZIP_DEFLATED)
    zipdir(dir_name, zipf)
    zipf.close()


# sftp creds sftp sftpuser@3.1.20.214   :   sftptestpass

def upload_and_delete(sftp, output_filename):
    print("************  Starting sftp upload and delete ************")
    with sftp.cd('uploads'):
        files_on_remote = sftp.listdir()
        sftp.put(output_filename, preserve_mtime=True)
        rm_files_list = filter_files_on_limit(files_on_remote, 20)
        # print(rm_files_list)
        for file in rm_files_list :
            sftp.remove(file)

    sftp.close()



if __name__ == '__main__':
    print("*********************************************************************")

    # print(sorted_ls(mypath,'mtime'))
    # print(sorted_ls(mypath,'ctime'))

    local_files = os.listdir(mypath)
    # print(local_files)
    rm_files_list = filter_files_on_limit(local_files, 2)
    # print(rm_files_list)

    ts = time.time()

    output_filename = "backup_"+str(int(ts))+".zip"
    output_filename_with_path = mypath + output_filename

    Zip(output_filename)

    sftp = pysftp.Connection('3.1.20.214', username='sftpuser', password='sftpuser')
    upload_and_delete(sftp, output_filename)
    delete_files(rm_files_list)
