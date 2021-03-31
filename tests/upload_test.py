# GoogleDrive認証設定
gauth = GoogleAuth()
gauth.CommandLineAuth()
drive = GoogleDrive(gauth)

# GoogleDrive共有フォルダID
MUSIC_FOLDER_ID = s.MUSIC_FOLDER_ID
VIDEO_FOLDER_ID = s.VIDEO_FOLDER_ID

    def test_file_search(self):
        print (self.title)
        self.file_id = drive.ListFile(
            {'q': 'title =\"' + self.title +  '\"'}
        ).GetList()[0]['id']

    def test_file_delete(self):
        test_file = drive.CreateFile()
        test_file['title']=self.title
        print (self.file_id)
        test_file.Delete(self.file_id)