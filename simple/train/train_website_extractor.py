from lxml import html
import requests

def getdepturetime(orgid,destid,day,month,year,hour):
    ##
    ##orgid- the station id which the trains depture
    ##destid- the station id which the train needs to arrive
    ##day-the day of the month of the ride
    ##moth-the month of the ride(number)
    ##year-the year of the ride(number)
    ##hour-the hour of the ride(number)
    allhours=[]
    #the list that will contain all the depture hours and will get returned

    page = requests.get(('https://www.rail.co.il/HE/DrivePlan/Pages/DrivePlan.aspx?DrivePlanPage=true&'
                         'OriginStationId={}&'
                         'DestStationId={}&'
                         'HoursDeparture={}&'
                         'MinutesDeparture=0&'
                         'GoingTrainCln={}-{}-{}&'
                         'IsFullURL=true').format(orgid,destid,hour,year,month,day))
    tree=html.fromstring(page.content)
    i=0
    hr=tree.xpath('//tr[@id="{}"]/td[position()=2]/text()'.format(i))
    ##loops thats exports the depture times until theres no depture times in the html file
    while(len(hr)!=0):
        allhours.append(hr[0])
        i=i+1
        hr=tree.xpath('//tr[@id="{}"]/td[position()=2]/text()'.format(i))


    return allhours
