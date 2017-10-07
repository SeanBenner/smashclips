# Smashclips
Automated highlights for Super Smash Bros Melee
----------------------------------------------
SSBM has grown a lot over the recent years.  There are a handful of people who, through tournament winnings, sponsorship salaray, and revenue from streaming, are able to lead a comfortable life playing this game for a living.  The game is only one piece of the larger Esports industry, which is expected to reach about 1.5 billion dollars by 2020.  That's still only a fraction of traditional sports, whose revenue is in the tens of billions, but I think that as Esports continues to grow there will be more and more parallels between the two. 

Thinking about these parallels, one similarity that came to mind was how both kinds of sports have their down times. Sportscenter is a popular show where fans can catch all the highlights of a game, however the same kind of highlights service doesn't exist in smash bros.  With Smashclips, the process of extracting interesting highlights of a match can be automated and highlights can be made out of any Youtube playlist.

------------------------------------------------
I used openCV, MoviePy, and Tesseract OCR to track the players health across a game.  To speed things, I only wanted to scan the area where the players' healths are, but as you can see in the images below, the healths are not always in the same place.  The two screen shots are from two different tournaments, where you can see the gameplay region switches from the left to the right side of the screen.  Even within the region, you can also see that the second player's health is slightly over to the right on the second image.  

![Fig. 1:  Finding the search area](images/search_areas.jpg?raw=true)

This is because they are using the third controller port on the console.  To solve this problem, I looked at the average frame of the video and used the percent sign for template matching.  From there, it's easy to define the search area as a small rectangle to the left of the percent sign.

![Fig. 2:  Defining the search area with template matching on the average frame of the video](images/Average_frames.jpg?raw=true)

Now that the search area is defined, there are a few preprocessing steps that must be taken to make the numbers readable by computer.  First is to convert the image to grayscale, next I applied a blur to the image to try to reduce any noise.  Next I binarized the image by setting all pixels to black or white depending on its intensity, and finally I applied a flood fill around the perimeter to fill in any gaps.  When it all works out nicely, it looks like the final frame below.

![Fig. 3:  Preprocessing steps](images/processing_steps.jpg?raw=true)

Once the video is processed, the frames and their OCR results are put into a Pandas dataframe.  I make a new column that measures the amount the health has changed since the last frame.  Most of the time this value is 0, but when it isn't, it's inferred that the character got hit.  To create a highlight, then, I use the algorithm below that looks for frequent occurrences of the health changing.  

![Fig. 4:  Highlight algorithm](images/highlight_algorithm.jpg?raw=true)

Sometimes the OCR is inaccurate due to the background noise of the image that can come through.  By restricing the algorithm to look for deltas in range of 3 to 30, it skips erroneous OCR results that might include an extra digit in the hundreds place that doesn't actually exist.  Despite this, the program is still able to extract some pretty cool highlights.  You can check out a couple of the results in the example clips folder.
----------------------------------------------------------
This project is only the beginning of what can be done for SSBM using computer vision.  I would like to improve the OCR accuracy so that I could confidently say the healths are exactly as measured.  I could then answer questions that have never been able to be answered, such as "at what percent is a player most likely to land a combo that takes the stock?" or "what's the average amount of damage done per combo?"  I'd like also like to add the ability to determine the characters and stage of a highlight.  I could then build a database of highlights that would be worthy of study similar to a chess database of tactics.  A user could search for combos done by/performed on specific characters and stages, just like how a chess player can search for games from a specific board state.  Lastly, being able to track the characters themselves would allow me to measure the distance and angle between the characters, which could provide insight into players' habits and tendancies, allowing players to eliminate their own predictable patterns and study those of their opponent's.  