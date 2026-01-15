#install.packages("randomcoloR")

library(readxl)
library(tolerance)
library("EnvStats")
library(RColorBrewer)
library(vioplot)
library(randomcoloR)
library(lubridate)
#==============================================================================
# pomocná filtrovací funkce
#==============================================================================
ff<-function(df,kom, om, lab, rn, start, end){
  if(kom == 0){kom<-df$kom}
  if(om == 0){om<-df$om}
  if(lab == 0){lab<-df$lab}
  if(start==0){start<-min(df$od)}
  if(end==0){end<-max(df$od)}
  if(rn==0){rn<-df$rn}
  f<-which(df$kom==kom & df$om==om & df$lab==lab & df$od>=start & df$od<=end & df$rn==rn)
  
  return(df[f,])
}
#==============================================================================
# Naètení dat
#==============================================================================
ScriptFolder<-dirname(rstudioapi::getSourceEditorContext()$path)
setwd(ScriptFolder)
setwd("../data/")
data <- read_excel("./Polozky_ZP/Spad 2023.xlsx", sheet=2, guess_max=21474836)

plat<-data$Platnost_b
kom_ID<-data$ID_Monit_položka_OM 
kom<-trimws(sapply(strsplit(data$Monitorovaná_položka_OM,"/"), tail, 1))
om<-data$Odbìrové_místo
om_ID<-data$ID_OM
lab<-data$Dodavatel_dat
a<-data$Hodnota
u<-data$Nejistota
jed<-data$Jednotka
mva<-data$Pod_MVA
od<-as.POSIXct(data$Datum_odberu_mistni_cas,format="%d.%m.%Y %H:%M",tz=Sys.timezone())
do<-as.POSIXct(data$Konec_odberu_mistni_cas,format="%d.%m.%Y %H:%M",tz=Sys.timezone())
rn<-data$Nuklid

tmpdf<-data.frame(plat,kom_ID,kom, om, om_ID, lab, a, u, mva, jed, od, do, rn, stringsAsFactors=FALSE)
tmpdf<-tmpdf[which(tmpdf$plat==1),]
#==============================================================================
# Nastavení filtru (0 = vše)
#==============================================================================

# dìlicí body pro referenèní a aktuální data:
newdata = "2023-01-01 00:00:00 CET"
olddata = "2013-01-01 00:00:00 CET"


kom = 0             # komodita
om = 0              # odbìrové místo
lab =  0            # dodavatel dat
start = 0           # èasový výbìr od
end = 0             # èasový výbìr do
rn = "Cs 137"       # radionuklid

all<-ff(tmpdf,kom, om, lab, rn, start, end)

# filtr na OM spady

all<-all[all$om %in% c("Brno", "Brno - Arboretum","Èeské Budìjovice - U nemocnice","Holešov - letištì",
                       "Hradec Králové - Piletice","Cheb - meteostanice","Kamenná","Ostrava - Syllabova",
                       "Plzeò - Klatovská", "Praha - Bartoškova","Ústí nad Labem - Habrovice","Bílá Hùrka",
                       "Dukovany","Hosty","Chlumec","Litoradlice","Moravsky Krumlov","Plástovice","Zálužice","Praha - Vypich"), ] 

all$year <- year(all$od)

new<-all[which(all$od>newdata),]
old<-all[which((all$od<=newdata)&(all$od>olddata)),]

newold<-all[which(all$od>olddata),]
newold<-newold[which(newold$a>0),]
newold<-newold[which(newold$a<1),]

#==============================================================================
# GRAFY
#==============================================================================
#==============================================================================
# èasová øada boxploty + kolmogorov-smirnov test
#==============================================================================

setwd("../reports/spady/")


group <- as.factor(newold$om)
labnames<-levels(group)
nlab <- length(labnames)

oms<-labnames
oms[which(oms=="Brno - Arboretum")]<-"BR"
oms[which(oms=="Èeské Budìjovice - U nemocnice")]<-"CB"
oms[which(oms=="Holešov - letištì")]<-"HOL"
oms[which(oms=="Ostrava - Syllabova")]<-"OVA"
oms[which(oms=="Praha - Bartoškova")]<-"PHA"
oms[which(oms=="Plzeò - Klatovská")]<-"PLZ"
oms[which(oms=="Ústí nad Labem - Habrovice")]<-"UL"
oms[which(oms=="Hradec Králové - Piletice")]<-"HK"
oms[which(oms=="Cheb - meteostanice")]<-"CHEB"
oms[which(oms=="Kamenná")]<-"KAM"
oms[which(oms=="Bílá Hùrka")]<-"BIH"
oms[which(oms=="Dukovany")]<-"DUK"
oms[which(oms=="Hosty")]<-"HOS"
oms[which(oms=="Chlumec")]<-"CHL"
oms[which(oms=="Litoradlice")]<-"LIT"
oms[which(oms=="Moravský Krumlov")]<-"MOK"
oms[which(oms=="Plástovice")]<-"PLA"
oms[which(oms=="Zálužice")]<-"ZAL"
oms[which(oms=="Praha - Vypich")]<-"VYP"

rnfile=gsub(" ", "", rn, fixed = TRUE)


colors_user <- c(rgb(0,0,0,1/4),rgb(1,0,0,1/4),rgb(0,0,1,1/4))
if(nlab==length(colors_user)){colors<-colors_user}
if(nlab>length(colors_user)){colors<-c(colors_user,distinctColorPalette(nlab-length(colors_user)))}
if(nlab<length(colors_user)){colors<-colors_user[1:nlab]}


ks <- ks.test(old$a,new$a)
stats<-paste("Spady Cs-137 - všechna data,   D-statistika = ",signif(as.numeric(ks[1]),4),";  p-hodnota = ",signif(as.numeric(ks[2]),4))
colnew="red"
jittercol <- rgb(0, 0, 255, max = 255, alpha = 50)
jittercolmva <- rgb(0, 255, 0, max = 255, alpha = 50)

if(ks$p.value>0.05){colnew<-"green"}


#=======================
# uložení do png souboru
#=======================

year <- newold$year
newoldmva<-newold[which(newold$mva==1),]
yearmva <- as.numeric(format(newoldmva$od,'%Y'))

pngfile = paste("spady_boxplot_vse_",rnfile,".png",sep="")
png(filename=pngfile,width = 1100, height = 800, units = "px")

colors = c(rep("grey",length(unique(newold$year))-1),colnew)
aind<-which(newold$mva==0)

boxplot(newold$a ~ newold$year, outline = FALSE,ylab="aktivita [Bq/m2]",xlab="Datum", col=colors,
        boxlwd = 2,whisklwd=2,staplelwd=2, cex.lab = 2, cex.axis=2, cex=2)
# stripchart(newold$a[aind] ~ newold$year[aind], vertical = TRUE, data = newold,
#            method = "jitter", add = TRUE, pch = 20, col = jittercol, cex=2)
# stripchart(newoldmva$a ~ yearmva, vertical = TRUE, data = newold,
# method = "jitter", add = TRUE, pch = 20, col = jittercolmva, cex=2)
mtext(stats, side=3, line=0, cex=2)
dev.off()


colors = c(rep("grey",length(unique(year))))
for (i in 1:nlab){
  
  pngfile = paste("spady_boxplot_",oms[i],"_",rnfile,".png",sep="")
  png(filename=pngfile,width = 800, height = 1000, units = "px")
  
  # filtrování dat podle odbìrového místa
  labind <- which(newold$om==labnames[i])
  aind<-which(newold$mva[labind]==0)
  a<-newold$a[labind]
  y<-year[labind]
  
  labindmva <- which(newoldmva$om==labnames[i])
  mva<-newoldmva$a[labindmva]
  ymva<-yearmva[labindmva]
  
  # velikost fontu a bodù
  font_size = 2
  point_size = 2
  
  # výpoèet toleranèních intervalù
  ti90<-normtol.int(newold$a[labind], alpha = 0.05, P = 0.90, side = 1, log.norm = TRUE)
  ti95<-normtol.int(newold$a[labind], alpha = 0.05, P = 0.95, side = 1, log.norm = TRUE)
  ti99<-normtol.int(newold$a[labind], alpha = 0.05, P = 0.99, side = 1, log.norm = TRUE)
  limits <- paste("Prùmìr = ", signif(mean(newold$a[labind]),3),";  TI90 = ",signif(ti90[5],3),";  TI95 = ",signif(ti95[5],3), ";  TI99 = ",signif(ti99[5],3),sep="")
  
  
  # konstrukce trojgrafu:
  par(mfrow=c(3,1), mai = c(1, 1, 0.25, 0.1))
  
  
  # boxplot + body
  boxplot(a ~ y, outline = FALSE,ylab="aktivita [Bq/m2]",xlab="Datum", col=colors, 
          cex.lab = font_size, cex.axis=font_size)
  # stripchart(a[aind] ~ y[aind], vertical = TRUE, 
  #            method = "jitter", add = TRUE, pch = 19, col = jittercol, cex=2)

  mtext(paste("Cs-137, Dodavatel dat: ",labnames[i]), side=3, line=0, cex=1.5)
  
  # èasová øada s toleranèními pásy
  
  plot(newold$od[labind],newold$a[labind], col= colors[1], pch = 19,  cex = 2, xlab="Datum", 
       ylab="aktivita [Bq/m2]",cex.lab = font_size, cex.axis=font_size)
  points(newold$od[labind],newold$a[labind], col = colors[i], pch=19,  cex = 2)
  points(newoldmva$od[labindmva],newoldmva$a[labindmva], col = jittercolmva, pch=19, cex = 2)
  abline(h=ti90[5], col = "blue")
  abline(h=ti95[5],col = "orange")
  abline(h=ti99[5], col = "red")
  mtext(limits, side=3, line=0, cex=1.5)
  
  yzoom <- as.numeric(ti99[5] * 1.15)
  
  plot(newold$od[labind],newold$a[labind], col= colors[1], cex = 2, pch = 19, xlab="Datum", 
       ylab="aktivita [Bq/m2]", ylim = c(0,yzoom), cex.lab = font_size, cex.axis=font_size)
  points(newold$od[labind],newold$a[labind], col = colors[i], cex = 2, pch = 19)
  points(newoldmva$od[labindmva],newoldmva$a[labindmva], col = jittercolmva, pch = 19, cex = 2)
  abline(h=ti90[5], col = "blue")
  abline(h=ti95[5],col = "orange")
  abline(h=ti99[5], col = "red")
  mtext(limits, side=3, line=0, cex=1.5)
  dev.off()
  
}

#==============================================================================
# lognormální qqplot s vyznaèenými aktuálními daty (necenzorovaná verze)
#==============================================================================

qq<-qqPlot(newold$a, distribution = "lnorm", param.list = list(mean = 0, sd = 1))
newold$typ<-"old"
newold$typ[which(newold$do>newdata)]<-"new"

dftyp <-data.frame(a=newold$a,typ=newold$typ)
dfsorted <- dftyp[order(dftyp$a),] 
indnew<-which(dfsorted$typ=="new")

pngfile = paste("spady_vse_qqplot_",rnfile,".png",sep="")
png(filename=pngfile,width = 1100, height = 800, units = "px")
plot(qq$x,qq$y, xlab="kvantily normálního rozdìlení", ylab="ln(aktivita) [Bq/m2]", pch=1,
     cex.lab = 2, cex.axis=2, cex=2)
points(qq$x[indnew],qq$y[indnew],col=rgb(red = 1, green = 0, blue = 0, alpha = 0.6), pch=0)
abline(mean(qq$y), sd(qq$y))
legend("topleft", legend=c("Referenèní data", "Aktuální data"), col=c("black", "red"), 
       pch=c(1,0),cex=2)
meta<-paste("Spady  všechna data   ",rn, "   Data od:", as.Date(newdata), "    Ref. data od: ", as.Date(olddata),sep=" ")
mtext(meta, side=3, line=0, cex=2)
dev.off()


group <- as.factor(newold$om)
labnmes<-levels(group)
nlab <- length(labnames)

oms<-labnames
oms[which(oms=="Brno - Arboretum")]<-"BR"
oms[which(oms=="Èeské Budìjovice - U nemocnice")]<-"CB"
oms[which(oms=="Holešov - letištì")]<-"HOL"
oms[which(oms=="Ostrava - Syllabova")]<-"OVA"
oms[which(oms=="Praha - Bartoškova")]<-"PHA"
oms[which(oms=="Plzeò - Klatovská")]<-"PLZ"
oms[which(oms=="Ústí nad Labem - Habrovice")]<-"UL"
oms[which(oms=="Hradec Králové - Piletice")]<-"HK"
oms[which(oms=="Cheb - meteostanice")]<-"CHEB"
oms[which(oms=="Kamenná")]<-"KAM"
oms[which(oms=="Bílá Hùrka")]<-"BIH"
oms[which(oms=="Dukovany")]<-"DUK"
oms[which(oms=="Hosty")]<-"HOS"
oms[which(oms=="Chlumec")]<-"CHL"
oms[which(oms=="Litoradlice")]<-"LIT"
oms[which(oms=="Moravský Krumlov")]<-"MOK"
oms[which(oms=="Plástovice")]<-"PLA"
oms[which(oms=="Zálužice")]<-"ZAL"
oms[which(oms=="Praha - Vypich")]<-"VYP"

rnfile=gsub(" ", "", rn, fixed = TRUE)


for (i in 1:nlab){
  
  pngfile = paste("spady_qqplot",oms[i],"_",rnfile,".png",sep="")
  png(filename=pngfile,width = 1100, height = 800, units = "px")
  labdf<-newold[which(newold$om==labnames[i]),]
  qq<-qqPlot(labdf$a, distribution = "lnorm", param.list = list(mean = 0, sd = 1))
  labdf$typ<-"old"
  labdf$typ[which(labdf$do>newdata)]<-"new"
  
  dftyp <-data.frame(a=labdf$a,typ=labdf$typ)
  dfsorted <- dftyp[order(dftyp$a),] 
  indnew<-which(dfsorted$typ=="new")
  
  plot(qq$x,qq$y, xlab="kvantily normálního rozdìlení", ylab="ln(aktivita) [Bq/m2]", pch=1,
       cex.lab = 2, cex.axis=2, cex=2)
  points(qq$x[indnew],qq$y[indnew],col=rgb(red = 1, green = 0, blue = 0, alpha = 0.6), pch=0)
  abline(mean(qq$y), sd(qq$y))
  legend("topleft", legend=c("Referenèní data", "Aktuální data"), col=c("black", "red"), pch=c(1,0),cex=2)
  meta<-paste("Spady  ",oms[i]," ",rn, "   Data od:", as.Date(newdata), "    Ref. data od: ", as.Date(olddata),sep=" ")
  mtext(meta, side=3, line=0, cex=2)
  dev.off()
}


#==============================================================================
# Pb 210
#==============================================================================
#==============================================================================
# Nastavení filtru (0 = vše)
#==============================================================================

# dìlicí body pro referenèní a aktuální data:
newdata = "2023-01-01 00:00:00 CET"
olddata = "2013-01-01 00:00:00 CET"


kom = 0             # komodita
om = 0              # odbìrové místo
lab =  0            # dodavatel dat
start = 0           # èasový výbìr od
end = 0             # èasový výbìr do
rn = "Pb 210"        # radionuklid

rnfile<-gsub(" ", "", rn, fixed = TRUE)
all<-ff(tmpdf,kom, om, lab, rn, start, end)

# filtr na OM aerosoly

all<-all[all$om %in% c("Brno", "Brno - Arboretum","Èeské Budìjovice - U nemocnice","Holešov - letištì",
                       "Hradec Králové - Piletice","Cheb - meteostanice","Kamenná","Ostrava - Syllabova",
                       "Plzeò - Klatovská", "Praha - Bartoškova","Ústí nad Labem - Habrovice","Bílá Hùrka",
                       "Dukovany","Hosty","Chlumec","Litoradlice","Moravsky Krumlov","Plástovice","Zálužice","Praha - Vypich"), ] 

all$year <- year(all$od)

new<-all[which(all$od>newdata),]
old<-all[which((all$od<=newdata)&(all$od>olddata)),]

newold<-all[which(all$od>olddata),]
newold<-newold[which(newold$a>0),]
newold<-newold[which(newold$a<1),]


year <- newold$year
newoldmva<-newold[which(newold$mva==1),]
yearmva <- as.numeric(format(newoldmva$od,'%Y'))


pngfile = paste("spady_boxplot","_",rnfile,".png",sep="")
png(filename=pngfile,width = 1100, height = 1100, units = "px")

par(mfrow=c(2,1), mai = c(1, 1, 1, 0.1))

aind<-which(newold$mva==0)
boxplot(newold$a ~ newold$year, outline = FALSE,ylab="aktivita [Bq/m2]",xlab="Datum", col=colors,
        boxlwd = 2,whisklwd=2,staplelwd=2, cex.lab = 2, cex.axis=2, cex=2)
# stripchart(newold$a[aind] ~ newold$year[aind], vertical = TRUE, data = newold, 
#            method = "jitter", add = TRUE, pch = 20, col = jittercol, cex=2)
# stripchart(newoldmva$a ~ yearmva, vertical = TRUE, data = newold, 
#            method = "jitter", add = TRUE, pch = 20, col = jittercolmva, cex=2)
mtext(stats, side=3, line=0, cex=2)
mtext("Pb-210", side=3, line=2, cex=1.5)


# výpoèet toleranèních intervalù
ti90<-normtol.int(newold$a, alpha = 0.05, P = 0.90, side = 1, log.norm = TRUE)
ti95<-normtol.int(newold$a, alpha = 0.05, P = 0.95, side = 1, log.norm = TRUE)
ti99<-normtol.int(newold$a, alpha = 0.05, P = 0.99, side = 1, log.norm = TRUE)
limits <- paste("Prùmìr = ", signif(mean(newold$a),3),";  TI90 = ",signif(ti90[5],3),";  TI95 = ",signif(ti95[5],3), ";  TI99 = ",signif(ti99[5],3),sep="")
yzoom <- as.numeric(ti99[5] * 1.15)

# èasová øada s toleranèními pásy

plot(newold$od,newold$a, col= "grey", pch = 19,  cex = 2, xlab="Datum", 
     ylab="aktivita [Bq/m2]",cex.lab = font_size, cex.axis=font_size)
points(newoldmva$od,newoldmva$a, col = jittercolmva, pch=19, cex = 2)
abline(h=ti90[5], col = "blue")
abline(h=ti95[5],col = "orange")
abline(h=ti99[5], col = "red")
mtext(limits, side=3, line=0, cex=1.5)
mtext("Pb-210", side=3, line=2, cex=1.5)
dev.off()




#==============================================================================
# K 40
#==============================================================================
#==============================================================================
# Nastavení filtru (0 = vše)
#==============================================================================

# dìlicí body pro referenèní a aktuální data:
newdata = "2023-01-01 00:00:00 CET"
olddata = "2013-01-01 00:00:00 CET"


kom = 0             # komodita
om = 0              # odbìrové místo
lab =  0            # dodavatel dat
start = 0           # èasový výbìr od
end = 0             # èasový výbìr do
rn = "K 40"        # radionuklid

rnfile<-gsub(" ", "", rn, fixed = TRUE)
all<-ff(tmpdf,kom, om, lab, rn, start, end)

# filtr na OM aerosoly

all<-all[all$om %in% c("Brno", "Brno - Arboretum","Èeské Budìjovice - U nemocnice","Holešov - letištì",
                       "Hradec Králové - Piletice","Cheb - meteostanice","Kamenná","Ostrava - Syllabova",
                       "Plzeò - Klatovská", "Praha - Bartoškova","Ústí nad Labem - Habrovice","Bílá Hùrka",
                       "Dukovany","Hosty","Chlumec","Litoradlice","Moravsky Krumlov","Plástovice","Zálužice","Praha - Vypich"), ] 

all$year <- year(all$od)

new<-all[which(all$od>newdata),]
old<-all[which((all$od<=newdata)&(all$od>olddata)),]

newold<-all[which(all$od>olddata),]
newold<-newold[which(newold$a>0),]
newold<-newold[which(newold$a<1),]


year <- newold$year
newoldmva<-newold[which(newold$mva==1),]
yearmva <- as.numeric(format(newoldmva$od,'%Y'))


pngfile = paste("spady_boxplot","_",rnfile,".png",sep="")
png(filename=pngfile,width = 1100, height = 1100, units = "px")

par(mfrow=c(2,1), mai = c(1, 1, 1, 0.1))

aind<-which(newold$mva==0)
boxplot(newold$a ~ newold$year, outline = FALSE,ylab="aktivita [Bq/m2]",xlab="Datum", col=colors,
        boxlwd = 2,whisklwd=2,staplelwd=2, cex.lab = 2, cex.axis=2, cex=2)
# stripchart(newold$a[aind] ~ newold$year[aind], vertical = TRUE, data = newold, 
#            method = "jitter", add = TRUE, pch = 20, col = jittercol, cex=2)
# stripchart(newoldmva$a ~ yearmva, vertical = TRUE, data = newold, 
#            method = "jitter", add = TRUE, pch = 20, col = jittercolmva, cex=2)
mtext(stats, side=3, line=0, cex=1.5)
mtext("K-40", side=3, line=2, cex=1.5)


# výpoèet toleranèních intervalù
ti90<-normtol.int(newold$a, alpha = 0.05, P = 0.90, side = 1, log.norm = TRUE)
ti95<-normtol.int(newold$a, alpha = 0.05, P = 0.95, side = 1, log.norm = TRUE)
ti99<-normtol.int(newold$a, alpha = 0.05, P = 0.99, side = 1, log.norm = TRUE)
limits <- paste("Prùmìr = ", signif(mean(newold$a),3),";  TI90 = ",signif(ti90[5],3),";  TI95 = ",signif(ti95[5],3), ";  TI99 = ",signif(ti99[5],3),sep="")
yzoom <- max(as.numeric(ti99[5] * 1.15))

# èasová øada s toleranèními pásy
plot(newold$od,newold$a, col= "grey", pch = 19,  cex = 2, xlab="Datum", 
     ylab="aktivita [Bq/m2]",cex.lab = font_size, cex.axis=font_size)
points(newoldmva$od,newoldmva$a, col = jittercolmva, pch=19, cex = 2)
abline(h=ti90[5], col = "blue")
abline(h=ti95[5],col = "orange")
abline(h=ti99[5], col = "red")
mtext(limits, side=3, line=0, cex=1.5)
mtext("K-40", side=3, line=2, cex=1.5)
dev.off()

#==============================================================================
# Ra 226
#==============================================================================
#==============================================================================
# Nastavení filtru (0 = vše)
#==============================================================================

# dìlicí body pro referenèní a aktuální data:
newdata = "2023-01-01 00:00:00 CET"
olddata = "2013-01-01 00:00:00 CET"


kom = 0             # komodita
om = 0              # odbìrové místo
lab =  0            # dodavatel dat
start = 0           # èasový výbìr od
end = 0             # èasový výbìr do
rn = "Ra 226"        # radionuklid

rnfile<-gsub(" ", "", rn, fixed = TRUE)
all<-ff(tmpdf,kom, om, lab, rn, start, end)

# filtr na OM aerosoly

all<-all[all$om %in% c("Kamenná","Plástovice","Zálužice"), ] 

all$year <- year(all$od)

new<-all[which(all$od>newdata),]
old<-all[which((all$od<=newdata)&(all$od>olddata)),]

newold<-all[which(all$od>olddata),]
newold<-newold[which(newold$a>0),]
newold<-newold[which(newold$a<1),]


year <- newold$year
newoldmva<-newold[which(newold$mva==1),]
yearmva <- as.numeric(format(newoldmva$od,'%Y'))


pngfile = paste("spady_boxplot","_",rnfile,".png",sep="")
png(filename=pngfile,width = 1100, height = 1100, units = "px")

par(mfrow=c(2,1), mai = c(1, 1, 1, 0.1))

aind<-which(newold$mva==0)
boxplot(newold$a ~ newold$year, outline = FALSE,ylab="aktivita [Bq/m2]",xlab="Datum", col=colors,
        boxlwd = 2,whisklwd=2,staplelwd=2, cex.lab = 2, cex.axis=2, cex=2)
# stripchart(newold$a[aind] ~ newold$year[aind], vertical = TRUE, data = newold, 
#            method = "jitter", add = TRUE, pch = 20, col = jittercol, cex=2)
# stripchart(newoldmva$a ~ yearmva, vertical = TRUE, data = newold, 
#            method = "jitter", add = TRUE, pch = 20, col = jittercolmva, cex=2)
mtext(stats, side=3, line=0, cex=1.5)
mtext("Ra-226", side=3, line=2, cex=1.5)


# výpoèet toleranèních intervalù
ti90<-normtol.int(newold$a, alpha = 0.05, P = 0.90, side = 1, log.norm = TRUE)
ti95<-normtol.int(newold$a, alpha = 0.05, P = 0.95, side = 1, log.norm = TRUE)
ti99<-normtol.int(newold$a, alpha = 0.05, P = 0.99, side = 1, log.norm = TRUE)
limits <- paste("Prùmìr = ", signif(mean(newold$a),3),";  TI90 = ",signif(ti90[5],3),";  TI95 = ",signif(ti95[5],3), ";  TI99 = ",signif(ti99[5],3),sep="")
yzoom <- as.numeric(ti99[5] * 1.15)

# èasová øada s toleranèními pásy
plot(newold$od,newold$a, col= "grey", pch = 19,  cex = 2, xlab="Datum", 
     ylab="aktivita [Bq/m2]",cex.lab = font_size, cex.axis=font_size)
points(newoldmva$od,newoldmva$a, col = jittercolmva, pch=19, cex = 2)
abline(h=ti90[5], col = "blue")
abline(h=ti95[5],col = "orange")
abline(h=ti99[5], col = "red")
mtext(limits, side=3, line=0, cex=1.5)
mtext("Ra-226", side=3, line=2, cex=1.5)
dev.off()

#==============================================================================
# Ra 226 - podle lokalit
#==============================================================================
newdata = "2023-01-01 00:00:00 CET"
olddata = "2013-01-01 00:00:00 CET"

kom = 0             # komodita
om = 0              # odbìrové místo
lab =  0            # dodavatel dat
start = 0           # èasový výbìr od
end = 0             # èasový výbìr do
rn = "Ra 226"       # radionuklid

all<-ff(tmpdf,kom, om, lab, rn, start, end)

# filtr na OM

all<-all[all$om %in% c("Kamenná","Plástovice","Zálužice"), ] 

all$year <- year(all$od)

new<-all[which(all$od>newdata),]
old<-all[which((all$od<=newdata)&(all$od>olddata)),]

newold<-all[which(all$od>olddata),]
newold<-newold[which(newold$a>0),]
newold<-newold[which(newold$a<1),]

group <- as.factor(newold$om)
labnames<-levels(group)
nlab <- length(labnames)

oms<-labnames
oms[which(oms=="Kamenná")]<-"KAM"
oms[which(oms=="Plástovice")]<-"PLA"
oms[which(oms=="Zálužice")]<-"ZAL"

rnfile=gsub(" ", "", rn, fixed = TRUE)


colors_user <- c(rgb(0,0,0,1/4),rgb(1,0,0,1/4),rgb(0,0,1,1/4))
if(nlab==length(colors_user)){colors<-colors_user}
if(nlab>length(colors_user)){colors<-c(colors_user,distinctColorPalette(nlab-length(colors_user)))}
if(nlab<length(colors_user)){colors<-colors_user[1:nlab]}


ks <- ks.test(old$a,new$a)
stats<-paste("Spady Ra-226 - všechna data,   D-statistika = ",signif(as.numeric(ks[1]),4),";  p-hodnota = ",signif(as.numeric(ks[2]),4))
colnew="red"
jittercol <- rgb(0, 0, 255, max = 255, alpha = 50)
jittercolmva <- rgb(0, 255, 0, max = 255, alpha = 50)

if(ks$p.value>0.05){colnew<-"green"}

year <- newold$year
newoldmva<-newold[which(newold$mva==1),]
yearmva <- as.numeric(format(newoldmva$od,'%Y'))

pngfile = paste("spady_boxplot_vse_",rnfile,".png",sep="")
png(filename=pngfile,width = 1100, height = 800, units = "px")

aind<-which(newold$mva==0)
colors = c(rep("grey",length(unique(newold$year))-1),colnew)
boxplot(newold$a ~ newold$year, outline = FALSE,ylab="aktivita [Bq/m2]",xlab="Datum", col=colors,
        boxlwd = 2,whisklwd=2,staplelwd=2, cex.lab = 2, cex.axis=2, cex=2)
# stripchart(newold$a[aind] ~ newold$year[aind], vertical = TRUE, data = newold, 
#            method = "jitter", add = TRUE, pch = 20, col = jittercol)
# stripchart(newoldmva$a ~ yearmva, vertical = TRUE, data = newold, 
#            method = "jitter", add = TRUE, pch = 20, col = jittercolmva)

mtext(stats, side=3, line=0, cex=2)
dev.off()


colors = c(rep("grey",length(unique(year))))
for (i in 1:nlab){
  
  pngfile = paste("spady_boxplot_",oms[i],"_",rnfile,".png",sep="")
  png(filename=pngfile,width = 800, height = 1000, units = "px")
  
  # filtrování dat podle odbìrového místa
  labind <- which(newold$om==labnames[i])
  a<-newold$a[labind]
  y<-year[labind]
  
  labindmva <- which(newoldmva$om==labnames[i])
  mva<-newoldmva$a[labindmva]
  ymva<-yearmva[labindmva]
  
  # velikost fontu a bodù
  font_size = 2
  point_size = 2
  
  # výpoèet toleranèních intervalù
  ti90<-normtol.int(newold$a[labind], alpha = 0.05, P = 0.90, side = 1, log.norm = TRUE)
  ti95<-normtol.int(newold$a[labind], alpha = 0.05, P = 0.95, side = 1, log.norm = TRUE)
  ti99<-normtol.int(newold$a[labind], alpha = 0.05, P = 0.99, side = 1, log.norm = TRUE)
  limits <- paste("Prùmìr = ", signif(mean(newold$a[labind]),3),";  TI90 = ",signif(ti90[5],3),";  TI95 = ",signif(ti95[5],3), ";  TI99 = ",signif(ti99[5],3),sep="")
  
  
  # konstrukce trojgrafu:
  par(mfrow=c(3,1), mai = c(1, 1, 0.25, 0.1))
  
  
  # boxplot + body
  boxplot(a ~ y, outline = FALSE,ylab="aktivita [Bq/m2]",xlab="Datum", col=colors, 
          cex.lab = font_size, cex.axis=font_size)
  # stripchart(a ~ y, vertical = TRUE, 
  #            method = "jitter", add = TRUE, pch = 19, col = jittercol, cex=2)

  mtext(paste("Ra-226, Dodavatel dat: ",labnames[i]), side=3, line=0, cex=1.5)
  
  # èasová øada s toleranèními pásy
  
  plot(newold$od[labind],newold$a[labind], col= colors[1], pch = 19,  cex = 2, xlab="Datum", 
       ylab="aktivita [Bq/m2]",cex.lab = font_size, cex.axis=font_size)
  points(newold$od[labind],newold$a[labind], col = colors[i], pch=19,  cex = 2)
  points(newoldmva$od[labindmva],newoldmva$a[labindmva], col = jittercolmva, pch=19, cex = 2)
  abline(h=ti90[5], col = "blue")
  abline(h=ti95[5],col = "orange")
  abline(h=ti99[5], col = "red")
  mtext(limits, side=3, line=0, cex=1.5)
  
  yzoom <- as.numeric(ti99[5] * 1.15)
  
  plot(newold$od[labind],newold$a[labind], col= colors[1], cex = 2, pch = 19, xlab="Datum", 
       ylab="aktivita [Bq/m2]", cex.lab = font_size, cex.axis=font_size)
  points(newold$od[labind],newold$a[labind], col = colors[i], cex = 2, pch = 19)
  points(newoldmva$od[labindmva],newoldmva$a[labindmva], col = jittercolmva, pch = 19, cex = 2)
  abline(h=ti90[5], col = "blue")
  abline(h=ti95[5],col = "orange")
  abline(h=ti99[5], col = "red")
  mtext(limits, side=3, line=0, cex=1.5)
  dev.off()
  
}


#==============================================================================
# U 234
#==============================================================================
#==============================================================================
# Nastavení filtru (0 = vše)
#==============================================================================

# dìlicí body pro referenèní a aktuální data:
newdata = "2023-01-01 00:00:00 CET"
olddata = "2013-01-01 00:00:00 CET"


kom = 0             # komodita
om = 0              # odbìrové místo
lab =  0            # dodavatel dat
start = 0           # èasový výbìr od
end = 0             # èasový výbìr do
rn = "U 234"        # radionuklid

rnfile<-gsub(" ", "", rn, fixed = TRUE)
all<-ff(tmpdf,kom, om, lab, rn, start, end)

# filtr na OM aerosoly

all<-all[all$om %in% c("Brno", "Brno - Arboretum","Èeské Budìjovice - U nemocnice","Holešov - letištì",
                       "Hradec Králové - Piletice","Cheb - meteostanice","Kamenná","Ostrava - Syllabova",
                       "Plzeò - Klatovská", "Praha - Bartoškova","Ústí nad Labem - Habrovice","Bílá Hùrka",
                       "Dukovany","Hosty","Chlumec","Litoradlice","Moravsky Krumlov","Plástovice","Zálužice","Praha - Vypich"), ] 

all$year <- year(all$od)

new<-all[which(all$od>newdata),]
old<-all[which((all$od<=newdata)&(all$od>olddata)),]

newold<-all[which(all$od>olddata),]
newold<-newold[which(newold$a>0),]
newold<-newold[which(newold$a<1),]


year <- newold$year
newoldmva<-newold[which(newold$mva==1),]
yearmva <- as.numeric(format(newoldmva$od,'%Y'))


pngfile = paste("spady_boxplot","_",rnfile,".png",sep="")
png(filename=pngfile,width = 1100, height = 1100, units = "px")

par(mfrow=c(2,1), mai = c(1, 1, 1, 0.1))

aind<-which(newold$mva==0)
boxplot(newold$a ~ newold$y, outline = FALSE,ylab="aktivita [Bq/m2]",xlab="Datum", col=colors,
        boxlwd = 2,whisklwd=2,staplelwd=2, cex.lab = 2, cex.axis=2, cex=2)
# stripchart(newold$a[aind] ~ newold$y[aind], vertical = TRUE, data = newold, 
#            method = "jitter", add = TRUE, pch = 20, col = jittercol, cex=2)
mtext(stats, side=3, line=0, cex=1.5)
mtext("U-234", side=3, line=2, cex=1.5)


# výpoèet toleranèních intervalù
ti90<-normtol.int(newold$a, alpha = 0.05, P = 0.90, side = 1, log.norm = TRUE)
ti95<-normtol.int(newold$a, alpha = 0.05, P = 0.95, side = 1, log.norm = TRUE)
ti99<-normtol.int(newold$a, alpha = 0.05, P = 0.99, side = 1, log.norm = TRUE)
limits <- paste("Prùmìr = ", signif(mean(newold$a),3),";  TI90 = ",signif(ti90[5],3),";  TI95 = ",signif(ti95[5],3), ";  TI99 = ",signif(ti99[5],3),sep="")
yzoom <- as.numeric(ti99[5] * 1.15)

# èasová øada s toleranèními pásy
plot(newold$od,newold$a, col= "grey", pch = 19,  cex = 2, xlab="Datum", 
     ylab="aktivita [Bq/m2]",cex.lab = font_size, cex.axis=font_size)
points(newoldmva$od,newoldmva$a, col = jittercolmva, pch=19, cex = 2)
abline(h=ti90[5], col = "blue")
abline(h=ti95[5],col = "orange")
abline(h=ti99[5], col = "red")
mtext(limits, side=3, line=0, cex=1.5)
mtext("U-234", side=3, line=2, cex=1.5)
dev.off()

#==============================================================================
# U 238
#==============================================================================
#==============================================================================
# Nastavení filtru (0 = vše)
#==============================================================================

# dìlicí body pro referenèní a aktuální data:
newdata = "2023-01-01 00:00:00 CET"
olddata = "2013-01-01 00:00:00 CET"


kom = 0             # komodita
om = 0              # odbìrové místo
lab =  0            # dodavatel dat
start = 0           # èasový výbìr od
end = 0             # èasový výbìr do
rn = "U 238"        # radionuklid

rnfile<-gsub(" ", "", rn, fixed = TRUE)
all<-ff(tmpdf,kom, om, lab, rn, start, end)

# filtr na OM aerosoly

all<-all[all$om %in% c("Brno", "Brno - Arboretum","Èeské Budìjovice - U nemocnice","Holešov - letištì",
                       "Hradec Králové - Piletice","Cheb - meteostanice","Kamenná","Ostrava - Syllabova",
                       "Plzeò - Klatovská", "Praha - Bartoškova","Ústí nad Labem - Habrovice","Bílá Hùrka",
                       "Dukovany","Hosty","Chlumec","Litoradlice","Moravsky Krumlov","Plástovice","Zálužice","Praha - Vypich"), ] 

all$year <- year(all$od)

new<-all[which(all$od>newdata),]
old<-all[which((all$od<=newdata)&(all$od>olddata)),]

newold<-all[which(all$od>olddata),]
newold<-newold[which(newold$a>0),]
newold<-newold[which(newold$a<1),]


year <- newold$year
newoldmva<-newold[which(newold$mva==1),]
yearmva <- as.numeric(format(newoldmva$od,'%Y'))


pngfile = paste("spady_boxplot","_",rnfile,".png",sep="")
png(filename=pngfile,width = 1100, height = 1100, units = "px")

par(mfrow=c(2,1), mai = c(1, 1, 1, 0.1))

aind<-which(newold$mva==0)
boxplot(newold$a ~ newold$y, outline = FALSE,ylab="aktivita [Bq/m2]",xlab="Datum", col=colors,
        boxlwd = 2,whisklwd=2,staplelwd=2, cex.lab = 2, cex.axis=2, cex=2)
# stripchart(newold$a[aind] ~ newold$y[aind], vertical = TRUE, data = newold, 
#            method = "jitter", add = TRUE, pch = 20, col = jittercol, cex=2)
mtext(stats, side=3, line=0, cex=1.5)
mtext("U-238", side=3, line=2, cex=1.5)


# výpoèet toleranèních intervalù
ti90<-normtol.int(newold$a, alpha = 0.05, P = 0.90, side = 1, log.norm = TRUE)
ti95<-normtol.int(newold$a, alpha = 0.05, P = 0.95, side = 1, log.norm = TRUE)
ti99<-normtol.int(newold$a, alpha = 0.05, P = 0.99, side = 1, log.norm = TRUE)
limits <- paste("Prùmìr = ", signif(mean(newold$a),3),";  TI90 = ",signif(ti90[5],3),";  TI95 = ",signif(ti95[5],3), ";  TI99 = ",signif(ti99[5],3),sep="")
yzoom <- as.numeric(ti99[5] * 1.15)

# èasová øada s toleranèními pásy
plot(newold$od,newold$a, col= "grey", pch = 19,  cex = 2, xlab="Datum", 
     ylab="aktivita [Bq/m2]",cex.lab = font_size, cex.axis=font_size)
points(newoldmva$od,newoldmva$a, col = jittercolmva, pch=19, cex = 2)
abline(h=ti90[5], col = "blue")
abline(h=ti95[5],col = "orange")
abline(h=ti99[5], col = "red")
mtext(limits, side=3, line=0, cex=1.5)
mtext("U-238", side=3, line=2, cex=1.5)
dev.off()

###############################

qq<-qqPlot(newold$a, distribution = "lnorm", param.list = list(mean = 0, sd = 1))
newold$typ<-"old"
newold$typ[which(newold$do>newdata)]<-"new"

dftyp <-data.frame(a=newold$a,typ=newold$typ)
dfsorted <- dftyp[order(dftyp$a),] 
indnew<-which(dfsorted$typ=="new")

pngfile = paste("spady_vse_qqplot_",rnfile,".png",sep="")
png(filename=pngfile,width = 1100, height = 800, units = "px")
plot(qq$x,qq$y, xlab="kvantily normálního rozdìlení", ylab="ln(aktivita) [Bq/m2]", pch=1,
     cex.lab = 2, cex.axis=2, cex=2)
points(qq$x[indnew],qq$y[indnew],col=rgb(red = 1, green = 0, blue = 0, alpha = 0.6), pch=0)
abline(mean(qq$y), sd(qq$y))
legend("topleft", legend=c("Referenèní data", "Aktuální data"), col=c("black", "red"), 
       pch=c(1,0),cex=2)
meta<-paste("Spady  všechna data   ",rn, "   Data od:", as.Date(newdata), "    Ref. data od: ", as.Date(olddata),sep=" ")
mtext(meta, side=3, line=0, cex=2)
dev.off()


group <- as.factor(newold$om)
labnmes<-levels(group)
nlab <- length(labnames)

oms<-labnames
oms[which(oms=="Brno - Arboretum")]<-"BR"
oms[which(oms=="Èeské Budìjovice - U nemocnice")]<-"CB"
oms[which(oms=="Holešov - letištì")]<-"HOL"
oms[which(oms=="Ostrava - Syllabova")]<-"OVA"
oms[which(oms=="Praha - Bartoškova")]<-"PHA"
oms[which(oms=="Plzeò - Klatovská")]<-"PLZ"
oms[which(oms=="Ústí nad Labem - Habrovice")]<-"UL"
oms[which(oms=="Hradec Králové - Piletice")]<-"HK"
oms[which(oms=="Cheb - meteostanice")]<-"CHEB"
oms[which(oms=="Kamenná")]<-"KAM"

rnfile=gsub(" ", "", rn, fixed = TRUE)


for (i in 1:nlab){
  
  pngfile = paste("spady_qqplot",oms[i],"_",rnfile,".png",sep="")
  png(filename=pngfile,width = 1100, height = 800, units = "px")
  labdf<-newold[which(newold$om==labnmes[i]),]
  qq<-qqPlot(labdf$a, distribution = "lnorm", param.list = list(mean = 0, sd = 1))
  labdf$typ<-"old"
  labdf$typ[which(labdf$do>newdata)]<-"new"
  
  dftyp <-data.frame(a=labdf$a,typ=labdf$typ)
  dfsorted <- dftyp[order(dftyp$a),] 
  indnew<-which(dfsorted$typ=="new")
  
  plot(qq$x,qq$y, xlab="kvantily normálního rozdìlení", ylab="ln(aktivita) [Bq/m2]", pch=1,
       cex.lab = 2, cex.axis=2, cex=2)
  points(qq$x[indnew],qq$y[indnew],col=rgb(red = 1, green = 0, blue = 0, alpha = 0.6), pch=0)
  abline(mean(qq$y), sd(qq$y))
  legend("topleft", legend=c("Referenèní data", "Aktuální data"), col=c("black", "red"), pch=c(1,0),cex=2)
  meta<-paste("Spady  ",oms[i]," ",rn, "   Data od:", as.Date(newdata), "    Ref. data od: ", as.Date(olddata),sep=" ")
  mtext(meta, side=3, line=0, cex=2)
  dev.off()
}



