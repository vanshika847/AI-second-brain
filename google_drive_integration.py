"""
Google Drive Integration for AI Second Brain
This module handles importing documents from Google Drive
"""

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload
import os
import io

# Scopes define what access we need
SCOPES = ['https://www.googleapis.com/auth/drive.readonly']

class GoogleDriveIntegration:
    def __init__(self):
        self.creds = None
        self.service = None
        
    def authenticate(self):
        """
        Authenticate with Google Drive using OAuth
        """
        # Check if we have saved credentials
        if os.path.exists('token.json'):
            self.creds = Credentials.from_authorized_user_file('token.json', SCOPES)
        
        # If no valid credentials, let user log in
        if not self.creds or not self.creds.valid:
            if self.creds and self.creds.expired and self.creds.refresh_token:
                self.creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(
                    'credentials.json', SCOPES)
                self.creds = flow.run_local_server(port=0)
            
            # Save credentials for next time
            with open('token.json', 'w') as token:
                token.write(self.creds.to_json())
        
        # Build the Drive service
        self.service = build('drive', 'v3', credentials=self.creds)
        print("✅ Successfully authenticated with Google Drive!")
        
    def list_files(self, folder_id=None, max_files=10):
        """
        List files from Google Drive
        
        Args:
            folder_id: Specific folder ID (optional)
            max_files: Maximum number of files to return
            
        Returns:
            List of file objects
        """
        try:
            # Build query
            query = f"'{folder_id}' in parents" if folder_id else None
            
            # Call the Drive API
            results = self.service.files().list(
                q=query,
                pageSize=max_files,
                fields="files(id, name, mimeType, size, createdTime)"
            ).execute()
            
            files = results.get('files', [])
            
            if not files:
                print('No files found.')
                return []
            
            print(f'Found {len(files)} files:')
            for file in files:
                print(f"  📄 {file['name']} ({file['mimeType']})")
            
            return files
            
        except Exception as e:
            print(f"❌ Error listing files: {str(e)}")
            return []
    
    def download_file(self, file_id, file_name):
        """
        Download a file from Google Drive
        
        Args:
            file_id: ID of the file to download
            file_name: Name to save the file as
            
        Returns:
            Path to downloaded file
        """
        try:
            request = self.service.files().get_media(fileId=file_id)
            
            # Create downloads folder if it doesn't exist
            os.makedirs('downloads', exist_ok=True)
            file_path = os.path.join('downloads', file_name)
            
            # Download the file
            fh = io.FileIO(file_path, 'wb')
            downloader = MediaIoBaseDownload(fh, request)
            
            done = False
            while done is False:
                status, done = downloader.next_chunk()
                print(f"Download {int(status.progress() * 100)}%")
            
            print(f"✅ Downloaded: {file_name}")
            return file_path
            
        except Exception as e:
            print(f"❌ Error downloading file: {str(e)}")
            return None
    
    def import_documents(self, folder_id=None):
        """
        Import all documents from Google Drive for processing
        
        Args:
            folder_id: Specific folder to import from (optional)
            
        Returns:
            List of downloaded file paths
        """
        if not self.service:
            print("❌ Not authenticated. Call authenticate() first.")
            return []
        
        # Get list of files
        files = self.list_files(folder_id=folder_id)
        
        downloaded_files = []
        
        # Download each file
        for file in files:
            # Only download text-based files
            supported_types = [
                'application/pdf',
                'text/plain',
                'application/vnd.google-apps.document',
                'application/msword',
                'application/vnd.openxmlformats-officedocument.wordprocessingml.document'
            ]
            
            if file['mimeType'] in supported_types:
                file_path = self.download_file(file['id'], file['name'])
                if file_path:
                    downloaded_files.append(file_path)
        
        print(f"\n✅ Imported {len(downloaded_files)} documents from Google Drive")
        return downloaded_files


# Example usage (for testing)
if __name__ == "__main__":
    print("🚀 Testing Google Drive Integration...\n")
    
    # Create integration instance
    drive = GoogleDriveIntegration()
    
    # Authenticate
    drive.authenticate()
    
    # List files
    print("\n📂 Your Google Drive files:")
    files = drive.list_files(max_files=5)
    
    # Uncomment to download files:
    # downloaded = drive.import_documents()