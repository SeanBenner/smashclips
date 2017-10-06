from match_processor import *
import boto
import os

if __name__ == '__main__':

    # Connect to S3
    access_key, access_secret_key = os.environ['AWS_ACCESS_KEY_ID'], os.environ['AWS_SECRET_ACCESS_KEY']
    conn = boto.connect_s3(access_key, access_secret_key)
    src = conn.get_bucket('smashclips')
    des = conn.get_bucket('tournamenthighlights')

    # Connect to postgresql
    user = os.environ['DBUSER']
    pw = os.environ['DBPW']
    db = os.environ['DBNAME']

    smash_con, meta = connect(user=user, password=pw, db=db, host='localhost', port=5432)



    # Loop through all videos in bucket
    for video in src.list():

        # Download video from boto
        try:
            match_name = video.name
            video.get_contents_to_filename('~/{}'.format(match_name))
            video.delete()
        except AttributeError:
            continue

        # Initialize video and data dictionary
        vid = VideoFileClip(match_name)
        data_store = {}

        # Get average frame and health areas
        img = get_average_image(vid)
        y_top, y_bottom, p1_x_left, p1_x_right, p2_x_left, p2_x_right = find_health_areas(img)

        frame_num = 0
        for frame in vid.iter_frames(progress_bar=False):
            frame_num += 1

            # Convert frame to gray and extract health areas
            grayFrame = cv2.cvtColor(frame, cv2.COLOR_RGB2GRAY)
            p1_area, p2_area = extract_health_area(grayFrame)

            # Blur health frames
            p1_area = cv2.medianBlur(p1_area, 5)
            p2_area = cv2.medianBlur(p2_area, 5)

            p1_area, p2_area = binarize_blurred_healths(p1_area, p2_area)

            # Get health with OCR
            p1h_ocr, p2h_ocr = ocr_health(p1_area, p2_area)

            data_store[frame_num] = (p1h_ocr, p2h_ocr)

        # Put data into dataframe and find combos
        df = raw_data_pipeline(data_store)
        p1_combos, p2_combos = find_combos(df)

        # Extract clips for P1 and P2.  p#_clips is a list of filenames
        p1_clips = extract_clips(p1_combos, 'P1', match_name)
        p2_clips = extract_clips(p2_combos, 'P2', match_name)

        # Initialize dataframe that will be written to SQL
        df_sql = pd.DataFrame(columns=['clip_name', 'deltas', 'total_damage'])

        # Initialize index of df_sql
        i = 0

        # Save clips to S3 and df_sql - P1
        for filename, combo in zip(p1_clips, p1_combos):
            new_clip = des.new_key(filename)
            new_clip.set_contents_from_filename(filename)
            os.remove(filename)
            df_sql.loc[i] = [filename, combo[2], sum(combo[2])]
            i += 1

        # Save clips to S3 and df_sql - P2
        for filename in p2_clips:
            new_clip = des.new_key(filename)
            new_clip.set_contents_from_filename(filename)
            os.remove(filename)
            df_sql.loc[i] = [filename, combo[2], sum(combo[2])]
            i += 1

        # Write df_sql to sql database
        df_sql.to_sql('highlights', smash_con, if_exists='append')

        # Remove video file from local drive
        os.remove(match_name)
