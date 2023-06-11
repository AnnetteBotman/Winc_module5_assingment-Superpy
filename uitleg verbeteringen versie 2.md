# Toelichting versie 2, doorgevoerde verbeteringen

### Verbeterpunten uit de video:

**Datum vooruit/achteruit zetten werkte niet goed.** 

Ik dacht dat ik dit goed had getest in versie 1, bleek helaas niet het geval. 

Is nu aangepast door het txt-bestand (t) met datum te lezen met toevoeging.rstrip() dus: t.read().rstrip

<br/>
<br/>

**Ivm met gebruikersvriendelijkheid bij het invoeren van gekochte producten "buydate" een optional argument maken**

Heb ik niet aangepast. De gebruiker kan mbv de functie 'time' de datum instellen op vandaag, enkele dagen vooruit/achteruit of iedere andere gewenste datum. 

Deze datum wordt als default gebruikt bij het invoeren van gekochte producten.

De gebruiker hoeft dus alleen maar productnaam, aantal, prijs en expirydate in te vullen.
Zolang de datum niet wordt aangepast met 'time', wordt bij iedere invoer de ingestelde datum gebruikt.
Is er bijvoorbeeld één product dat met een andere buydate ingevoerd moet worden, dan kan de gebruiker een datum intypen en vervolgens zoals gebruikelijk de overige gegevens van dat product, dus bijvoorbeeld: **2023-06-01&nbsp;&nbsp; apples&nbsp;&nbsp; 10&nbsp;&nbsp; 0.5&nbsp;&nbsp; 2023-06-30.**

Bij het volgende product wordt, indien geen datum wordt ingegeven, weer de ingestelde datum gebruikt.
Is dit niet gebruiksvriendelijk genoeg?

Voor de verkochte producten werkt dit hetzelfde. Dus eerst de datum instellen met 'time', vervolgens de productgegevens invoeren.

<br/>
<br/>

**Bij verkochte producten de gebruiker geen expirydate laten invoeren maar gebruik maken van deze gegevens uit de lijst met gekochte producten.**

Heb ik aangepast.

Had ik in eerste instantie niet zo ingericht omdat er meerdere inkoopbatches (meerdere dagen) van een product kunnen zijn met dezelfde expirydatum. Denk bijvoorbeeld aan producten met een lange houdbaarheidsdatum. Dan kunnen er bijvoorbeeld op maandag, woensdag en vrijdag pakken koffie zijn ingekocht met allemaal dezelfde expirydate. En het kunnen ook meerdere inkoopbatches zijn van hetzelfde product met andere expirydates. Het direct laten invoeren van de expirydate was wel zo makkelijk maar inderdaad niet zo gebruikersvriendelijk.

Ieder inkoop krijgt een unieke ID mee bij invoer in de bought.csv

Om goed overzicht van de voorraad te hebben moeten de verkochte producten gelinkt worden aan de juiste inkoopbatch. Ieder verkocht product krijgt een unieke ID én de inkoop_ID (buyid)

<br/>

Ik heb het nu zo geprogrammeerd:

Bij invoer van een product wordt eerst gezocht naar de productnaam:

- Is er 1 match, dan krijgt het product de buyid mee van die match en wordt het product toegevoegd aan de bought.csv. 

- Is er niet genoeg voorraad, wordt er melding van gemaakt en wordt het product niet toegevoegd aan de bought.csv.

- Is er geen match, wordt hier ook melding van gemaakt en wordt de gebruiker gevraagd de invoer te controleren.

- Zijn er meerdere expirydates, dan wordt de gebruiker gevraagd de datum in te voeren van de juiste expirydate. 

- Zijn er meerdere inkoopbatches met deze expirydate, dan wordt de inkoopbatch met het laagste ID eerst gebruikt om te koppelen aan het verkochte product. Zijn er dan nog producten over, worden die gekoppeld aan de volgende inkoopbatch.

Voor dit laatste is een aparte functie geschreven omdat deze herstart moet worden al naar gelang er nog producten over zijn die opnieuw gelinkt moeten worden aan een inkoopbatch. 

Daarvoor moet de voorraad eerst worden bijgewerkt.



 
