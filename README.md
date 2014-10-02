Opentrain community data analysis
========================================================================

כחלק מפרויקט רכבת פתוחה, הגשנו בקשה (וקיבלנו!) נתונים על זמני רכבות ל- 2013.
כאן מרוכזים הנתונים הללו יחד עם כלים בסיסיים לקריאה וניתוח שלהם. כל אחד מוזמן להוסיף קוד שמנתח את הנתונים ולהעלות אותו בחזרה לגיט. בקבוצת דיון של הסדנא ניתן להסביר את הניתוחים ולהפנות לקוד. אפשר לחשוב על זה בתור הרחבה של דיון לכזה שכולל כתיבת קוד. הגיט הופך למעין לוח מרכזי שכולם יכולים לראות ולכתוב עליו.

אנו מזמינים אתכם להשתמש בקוד הנ"ל ולספר לקהילה על הדבר הכי משמח ומרגיז שגיליתם בנתונים, או כל דבר אחר שאתם מוצאים.


Installation
============
Fork the project to your github account

Clone the project to a working directory:

    git clone git@github.com:YOUR-USER-NAME/OpenTrainCommunity.git

Run the install script:

    cd OpenTrainCommunity
    sudo ./install.sh

The last thing the install script does is to actually process the data,
so when you see output like:

    Extracting data files to /tmp/opentrain_data
    processing file 1 of 12 in 2013 data
    Done 5%
    Done 10%
    ...

you are on the right track. Now sit back and relax for about an hour :)
