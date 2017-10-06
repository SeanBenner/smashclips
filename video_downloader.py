import boto
import os
import pytube

if __name__ == '__main__':

    access_key, access_secret_key = os.environ['AWS_ACCESS_KEY_ID'], os.environ['AWS_SECRET_ACCESS_KEY']
    conn = boto.connect_s3(access_key, access_secret_key)
    bucket = conn.get_bucket('smashclips')

    with open('videos.txt') as f:
        vids = [line.rstrip('\n') for line in f]

    for url in vids:

        # Download the video and get the file name
        yt = pytube.YouTube(url)
        filename = yt.filename + '.mp4'
        try:
            video = yt.get('mp4', '720p')
        except 'DoesNotExist':
            continue
        video.download('~')

        # Add file to S3
        video_file = bucket.new_key(filename)
        video_file.set_contents_from_filename(filename)

        # Remove local file
        os.remove(filename)
