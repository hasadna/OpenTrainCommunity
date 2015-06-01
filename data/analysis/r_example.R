#_______________________________________________________________________________
# Name:        Open Train
# Purpose:
#
# Author:      Dean
#
# Created:     26/01/2015
# Copyright:   (c) Dean 2015
#_______________________________________________________________________________


#########                           Load Packages                      ######### 
#_______________________________________*______________________________________#
#List of library names to be used in the code
libnames<-c("caret","rpart","rpart.plot","rattle",
            "RPostgreSQL","dplyr","magrittr")
#---Install libraries
#sapply(libnames, FUN = function(x) {do.call("install.packages", list(x))})
#---Require libraries
invisible(lapply(libnames, require, character.only = TRUE))
#Clear Memory
rm(libnames)


#########                           Load Data                          ######### 
#_______________________________________*______________________________________#
#---Working Directory
  setwd("D:/Code/OpenTrain")
#**Load Binary R data frame####
  load("D:/Code/OpenTrain/TrainData.RData")
#XOR
#**Loading data from PostgreSQL server####
  #---Create Driver
  drv <- dbDriver("PostgreSQL")
  #---Open Connection
  con <- dbConnect(drv,
                   dbname  ="traindata",
                   host    ="104.131.88.144",
                   user    ="guest",
                   password="guest")
  #---Set Limit
  limit<-0
  limit<-ifelse(limit>0,paste("LIMIT",limit,sep=" "),";")
  #---Load Query
  query.file<-"TDquery.txt"
  # query.file<-"data_sample_reduced.txt"
  query<-paste(readChar(query.file,file.info(query.file)$size),
               limit,sep=" ")
  
  system.time(
    data<-dbGetQuery(con, query)
  )
  
  
#**Disconnect####
  dbDisconnect(con)

#########                           Data Prep                          #########  
#_______________________________________*______________________________________#
raw.data<-tbl_df(data)
head(data,30)
data <- arrange(raw.data,trip_name,index)
data<-data %>%
  mutate(depdelay = depdelay/60) %>%
  mutate(arrdelay = arrdelay/60) %>%
  mutate(dep_gt10 = (depdelay>=10)) %>%
  mutate(arr_gt10 = (arrdelay>=10)) %>%
  mutate(dow = weekdays(arrexpected)) %>%
  mutate(sch.rest = difftime (time1=depexpected, time2=arrexpected,units="mins")) %>%
  mutate(rest = difftime(time1 = depactual,time2 = arractual,units = "mins"))%>%
  mutate(gain = arrdelay - depdelay)
data$rest
names(data)
mean(data$sch.rest,na.rm=TRUE)
data[data$trip_name=="1006_20130120",c("sch.rest","gain")]
qplot(data$sch.rest)

#########                              EDA                             #########  
#_______________________________________*______________________________________#
s.data<-head(data,50000)


#########                           First Model                        #########  
#_______________________________________*______________________________________#


#########                           Second Model                       #########  
#_______________________________________*______________________________________#


#########                           Evaluation                         #########  
#_______________________________________*______________________________________#


#########                           Deployment                         #########  
#_______________________________________*______________________________________#
