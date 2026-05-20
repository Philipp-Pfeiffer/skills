# FBI Wanted API Details

## Subjects (Categories)

- Violent Crime - Murders
- Kidnappings and Missing Persons
- White-Collar Crime
- Counterintelligence
- Seeking Information
- Criminal Enterprise Investigations
- Ten Most Wanted Fugitives
- Endangered Child Alert Program
- ViCAP Unidentified Persons
- ViCAP Homicides and Sexual Assaults
- Additional Violent Crimes

## FBI Field Offices

- albany
- albuquerque
- boston
- billings
- chicago
- cincinnati
- cleveland
- dallas
- denver
- detroit
- elpaso
- houston
- indianapolis
- jackson
- jacksonville
- kansascity
- lasvegas
- losangeles
- louisville
- memphis
- miami
- milwaukee
- minneapolis
- mobile
- newark
- newhaven
- neworleans
- newyork
- norfolk
- oklahomacity
- omaha
- philadelphia
- phoenix
- pittsburgh
- portland
- quantico
- richmond
- sacramento
- saltlakecity
- sanantonio
- sandiego
- sanfrancisco
- seattle
- springfield
- stlouis
- tampa
- washingtondc

## Response Fields

| Field | Type | Description |
|-------|------|-------------|
| uid | string | Unique identifier |
| title | string | Full name |
| description | string | Short charge description |
| subjects | array | Categories |
| status | string | `na` (not arrested), `captured`, etc. |
| reward_text | string | Human-readable reward amount |
| caution | string | Detailed description of offense |
| dates_of_birth_used | array | Known DOBs |
| place_of_birth | string | Birth location |
| hair | string | Hair color |
| eyes | string | Eye color |
| height | string | Height |
| weight | string | Weight |
| sex | string | Sex |
| race | string | Race |
| nationality | string | Nationality |
| scars_and_marks | string | Distinguishing marks |
| ncic | string | NCIC number |
| field_offices | array | FBI offices handling the case |
| images | array | Photo objects with `large`, `thumb`, `caption` |
| files | array | PDF posters with `url`, `name` |
