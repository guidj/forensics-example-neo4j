# Forensics Example, using Neo4j

[Finding connections in data: multi-domain graphs](https://thinkingthread.com/connecting-data-with-multi-domain-graphs/)

## Generating data files

First, build the environment:

```
bash scripts/build-env.sh
```

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

## Seeding

Before seeding, make sure the connection settings on the `config.ini` file for Neo4j are correct.

To seed the data, run the `main.py` script with the flag `seed`:

```
app-env/bin/python src/forensics/main.py --seed yes 
```

This will delete existing data on the database, and seed new data.

## Running pattern analysis

```
app-env/bin/python src/forensics/main.py --pattern X
```

Where X is the pattern you want to find. Currently, there are 5 options:

    1: Find the top 20 people that took more than 1 flight between ~Jan - Jun 2014, to any destination.'
       Results are ordered by number of flights to each country',
    2: Find people that took more than 1 flight to any country each month, between ~Jan - Aug 2014',
    3: Find a phone number that has made calls on Wednesdays, between 6pm and 10pm to the representative of XYZ',
    4: Among the people that called the representative, find those that have flown in or out of one of enterprise XYZ offices in Japan, or the UK
    5: Among the people that called the representative, and flew in or out of one of Enterprise XYZ\'s subsidiaries, find those that have an employment history at WT Enterprises'
    
If you don't provide a value for X, all options are executed.


## Visualizing data

To visualize flights and phone call data, you first need to generate a small sample. 
The [prep.py](src/html/prep.py) script. It will create files that the [index.html](src/html/index.html) will use to generate
visualizations. You can then open the index.html file and visualize the randomly generated sample.
