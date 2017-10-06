# Smashclips
Automated highlights for Super Smash Bros Melee
----------------------------------------------
SSBM has grown a lot over the recent years.  There are a handful of people who, through tournament winnings, sponsorship salaray, and revenue from streaming, are able to lead a comfortable life playing this game for a living.  The game is only one piece of the larger Esports industry, which is expected to reach about 1.5 billion dollars by 2020.  That's still only a fraction of traditional sports, whose revenue is in the tens of billions, but I think that as Esports continues to grow there will be more and more parallels between the two. 

Thinking about these parallels, one similarity that came to mind was how both kinds of sports have their down times.  While Sportscenter exists where fans can catch all the highlights of a game, the same kind of highlights service doesn't in smash bros.  With Smashclips, the process of extracting interesting highlights of a match can be automated.
------------------------------------------------
I used openCV, MoviePy, and Tesseract OCR to track the players health across a game.  To speed things, I only wanted to scan the area where the players' healths are, but as you can see in the images below, the healths are not always in the same place.  The two screen shots are from two different tournaments, where you can see the gameplay region switches from the left to the right side of the screen.  Even within the region, you can also see that the second player's health is slightly over to the right on the second image.  




This is because they are using the third controller port on the