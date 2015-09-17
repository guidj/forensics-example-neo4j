#Forensics Example, using Neo4j

Finding patterns in data: multi-domain graphs

##Generating data files

Run the seed.py script: 

```
app-env/bin/python src/forensics/seed.py
```

Data fields:

**People**

  - **id**: Person ID, UUID4. Text
  - **number**: Phone number. Text.
  - **name**: Text
  - **sex**: Text, ['M', 'F']

**Calls**

  - **source**: Phone number where call originated from. Text
  - **target**: Phone number where call went to. Text
  - **weekday**: Weekday of call event. Number. Monday is 0, Sunday is 6
  - **timestamp**: Unix timestamp of the call. Number
  - **hour**: Hour of the call. Number, 0-23

**Flights**

  - **number**: Flight number. Text.
  - **person**: ID of person. UUID4. Text
  - **timestamp**: Time of flight departure. Unix timestamp. Number
  - **departure.country**: Country of departure. Text
  - **departure.city**: City/locality of departure. Text
  - **destination.country**: Country of destination. Text
  - **destination.city**: City/locality of destination. Text

**Employment**

  - **company**: Name of company. Text
  - **person**: ID of person. UUID4. Text
  - **since**: Date of employment. Unix timestamp. Number
  - **until**: Date employment ended. Number. -1 is for current employment

##Seeding

Before seeding, make sure the connection settings on the `config.ini` file for Neo4j are correct.

To seed the data, run the `main.py` script with the flag `seed`:

```
app-env/bin/python src/forensics/main.py --seed yes 
```

This will delete existing data on the database, and seed new data.

##Running pattern analysis

