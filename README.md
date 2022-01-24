# dang.io
Discord bot with focus on random Youtube videos

These days content on the internet becomes more and more slick and easy-to-digest. The way services like Youtube work makes it very hard to find 'raw' videos.   

This was not always the case. There was a time where people would host and upload stuff just because they wanted to, not to become a hotshot influencer. 
The Dang.io bot was created to celebrate these old times.

It's made to dig up the hard to digest footage. The non-clickbait. The spam. The screepcap video of some kid who has no idea what's going on. The video some person made, just because.

## First attempt
At first, the Youtube official API was used to find random videos. This turned out to be not very succesful, because Youtube pushes the content that is likely to cause engagement.
This is the opposite of what we want to dig up. It was left in there as a seperate command, because why not?

## The good stuff
Second approach was the `youtube_s module` (always written using underscore, never pure pascal case). This module performs an unholy ritual to unearth  the hidden 'gems' that not alot of people have laid there eyes upon.
After some finetuning, it's more successful than expected. It can bring joy to your Discord room by serving the best content - content for no one.
