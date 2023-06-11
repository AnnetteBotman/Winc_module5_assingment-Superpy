Rapport technische notities

### Buyid koppelen aan verkochte producten

Er kunnen op meerdere dagen producten zijn gekocht met eenzelfde expirydate. Daarvan kunnen op meerdere dagen producten zijn verkocht met een verschillende verkoopprijs ()denk aan aanbiedingen etc). 
Voor het bijhouden van de voorraad is het noodzakelijk de verkochte producten te linken aan  de juiste inkoopbatch. Iedere inkoop wordt voorzien van een unieke buyid, ieder verkocht product wordt voorzien van het bijbehorende buyid.

Dit is opgelost door bij invoer van een verkocht product in de bought.csv te zoeken naar de productnaam. Bij meerdere records (meerdere inkoopbatches van zelfde productproductnaam/expirydate), dient de gebruiker de juiste expirydate in te voeren. Vevolgens wordt, indien er meerdere inkoopbatches zijn met dezelfde expirydate, het eerste record gebruikt om de buyid toe te voegen en het aantal producten in voorraad te vergelijken met aantal verkochte producten. Is het aantal minder dan de voorraad, dan is de functie hiermee klaar, anders wordt voor het resterende aantal nogmaals de functie aangeroepen, en eventueel gebruik gemaakt van het volgende record van de inkoopbatch, om alle verkochte producten van een buyid te voorzien. Op die manier wordt ook een melding gegenereerd als het laatste product is verkocht.

### Exportfunctie
Voor ieder type rapport is een afzonderlijke functie geschreven; aan het einde van deze functies wordt de functie aangeroepen om de rapportgegevens te exporteren, dit is één en dezelfde functie. Als variabelen worden een directory, bestandsnaam en een ‘label’ meegegeven. 

Het had mijn voorkeur om ieder rapport met stdout weg te schrijven als ‘buffer’variabele en deze vervolgens in de export-functie te gebruiken. Ik kreeg het echter dan alleen voor elkaar om het rapport in de exportfunctie als csv-bestand te exporteren. 

Ik heb er voor gekozen om ieder rapport als een zelfoverschrijvend bestand in een aparte directory op te slaan. Er ontstaat dus geen bulk aan gegevens, er wordt steeds maar één bestand weggeschreven en overschreven. In eerste instantie dacht ik dat pickle gebruikt kon worden maar hiervoor werd gewaarschuwd dat het niet veilig zou zijn. Ben uiteindelijk op parquet uitgekomen.

### Validatie
Ik heb geprobeerd om alle mogelijke fouten zoveel mogelijk op te (laten) merken en op te laten lossen door de gebruiker tijdens de invoer zodat de lijsten van inkoop en verkoop kloppen:

- Iedere ingevoerde datum wordt gecheckt op het juiste format. Klopt dit niet, dan wordt hiervan een melding gemaakt en het product niet ingevoerd in de buy/sell lijst
- Bij invoer van ingekochte producten wordt gekeken of de inkoopdatum niet voorbij de expirydate ligt.
- Bij invoer van verkochte producten wordt gecheckt of de combinatie van product en expirydate aanwezig is in de gekochte productenlijst, zo niet volgt een melding en producten worden niet toegevoegd aan bought.csv
- Bij invoer van verkochte producten wordt gecheckt of het aantal dat wordt ingevoerd de voorraad niet overschrijdt. Hiervan wordt melding gemaakt en het product wordt niet ingevoerd in de lijst.
- Bij lege dataframes volgt geen foutmelding of print van lege tabel maar is het uitgeprogrameerd naar een alternatieve tabel of exit uit programma.
 
