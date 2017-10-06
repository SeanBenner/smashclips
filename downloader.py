import youParse

playlists = ["https://www.youtube.com/playlist?list=PLP6dKBTiEHygtGkKeL5YPeSJWLB5gUUB9", \
            "https://www.youtube.com/playlist?list=PLP6dKBTiEHyjR-e-M0iegor0-IJprS9Yd", \
            "https://www.youtube.com/playlist?list=PLP6dKBTiEHyizUR_JI7e9cKe1Jr5I6hv5", \
            "https://www.youtube.com/playlist?list=PLP6dKBTiEHyjDhTg6d7XucLtXJmpHAy0T", \
            "https://www.youtube.com/playlist?list=PLP6dKBTiEHygQORy0KALb4w4Qu6s6nRfl", \
            "https://www.youtube.com/playlist?list=PLP6dKBTiEHyiEziDA6xhd83fl2L9u3_Ap", \
            "https://www.youtube.com/playlist?list=PLP6dKBTiEHyg8K-mT1KJDTr5qhgjOdVG6", \
            "https://www.youtube.com/playlist?list=PLZV7WzjApoS3N62uUUKP6jhfHlCZHD819", \
            "https://www.youtube.com/playlist?list=PLe5nQdhHqwUW_Pb-xl2kV9BqMEe-P9o7q", \
            "https://www.youtube.com/playlist?list=PLGxurdcm7z4CjXEhFhOIP_bZTVFViaO0k", \
            "https://www.youtube.com/playlist?list=PLcxB0aILkJ_fXYk0N3dNLL0h7arPUY3WT", \
            "https://www.youtube.com/playlist?list=PLcMdMmtHkPpSczIwLdKrtLpbcR3Keswvq", \
            "https://www.youtube.com/playlist?list=PLqHTZ5qsD2QFHOMy83eBcdK4D53eSJjqG", \
            "https://www.youtube.com/playlist?list=PLcMdMmtHkPpRStg0ifHVPCD2z85B1Ge0k", \
            "https://www.youtube.com/playlist?list=PLQaCDKpI30PiLx1Nz5ndF2tsgo8Y-qEeJ", \
            "https://www.youtube.com/playlist?list=PLjqjFqIMEtWcYipgKhdsSxH_IMnc4vv9r", \
            "https://www.youtube.com/playlist?list=PLcMdMmtHkPpTFP3jIhz45zhaY04c6bA-A"]

for url in playlists:
    youParse.crawl(url)
