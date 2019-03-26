<h3>Table of Contents</h3>
    <ul>
        <li><a href='#head'>Changes to SParts Family</a></li>
        <ul>
            <li><a href='#general_change'>General Changes</a></li>
            <ul>
                <li><a href='#change'>Changes</a></li>
                <li><a href='#new_cmd'>New CMD calls</a></li>
            </ul>
            <li><a href='#specific_change'>Specific Changes</a></li>
            <ul>
                <li><a href='#cat_fam'>Category Family</a></li>
                <li><a href='#org_fam'>Organization Family</a></li>
                <li><a href='#pt_fam'>Part Family</a></li>
                <li><a href='#art_fam'>Artifact Family</a></li>
            </ul>
        </ul>    
    </ul>

#

<h1 id='head'>Changes to SParts Family</h1>

**_Note: all the changes that are made here are on the 'kernal' side of the sParts and no changes has been made on the 'application' side._**

**_Important: Users need to create their own personalized docker image via running 'docker-compose build'. First the user must uncomment lines 5-7 in docker-compose.yaml file._**

```
from

5|      #  build:
6|      #  context: .
7|      #  dockerfile: sParts.Dockerfile

to

5|        build:
6|        context: .
7|        dockerfile: sParts.Dockerfile
```

**_Once lines 5-7 are uncomment, make sure to uncomment everything in sParts.Dockerfile except line 4. Then call:_**

```bash
    $ docker-compose build
```

**_in the terminal. As of now, the image will be named 'phyohtut/sparts-test:part' since that is what is stored in line 8 of 'docker-compose.yaml' file._**

##

<h2 id='general_change'>General Changes</h2>

<h4 id='change'>Changes</h4>

* Data and Payloads are now stored as JSON rather than CSV for all the families except the 'User Family'.
* Admin will already register as soon as the docker-compose file is run by using:

```bash
    $ docker-compose down
    $ docker-compose up
```

* Test-script called 'lazy_user.py' will initialize first 57 blocks for the user to play around with kernal commands.
* Ability to amend states if mistakes were made.
* Ability to rebuild the states of the object associated with the specific uuid given a timeframe.
* UTC timestamp added for all the families.
* Fixes to compensate for the new data storage.
* Most of the logics are done in batch.py to reduce the workload on handler.py, validator. 

<h4 id='new_cmd'>New CMD calls</h4>

###### amend:

allows the permissioned users to amend the fields related to uuid.

```bash
    $ artifact amend {art_id} {art_alias} {art_name} {art_type} {art_checksum} {art_label} {art_openchain} {pri_key} {pub_key}
    $ organization amend {org_id} {org_alias} {org_name} {org_type} {org_description} {org_url} {pri_key} {pub_key}
    $ pt amend {pt_id} {pt_name} {pt_checksum} {pt_version} {pt_alias} {pt_license} {pt_label} {pt_description} {pri_key} {pub_key}
    $ category amend {cat_id} {cat_name} {description} {pri_key} {pub_key}
```

Note:

* At least one of the fields must be different from its pior state for the cmd to process successfully.
* The object that the user is trying to call this cmd on must be first created or the cmd will throw an error.

###### retrieve --all:

allows the user to get all the historical data regarding the specific uuid.

```bash
    $ artifact retrieve --all {art_id}
    $ organization retrieve --all {org_id}
    $ pt retrieve --all {pt_id}
    $ category retrieve --all {cat_id}
```

Note:

* The object that the user is trying to call this cmd on must exists or the cmd will throw an error.

###### retrieve --range:

allows the user to get all the historical data regarding the specific uuid within the specified range.

```bash
    $ artifact retrieve --range yyyymmdd yyyymmdd {art_id}
    $ organization retrieve --range yyyymmdd yyyymmdd {org_id}
    $ pt retrieve --range yyyymmdd yyyymmdd {pt_id}
    $ category retrieve --range yyyymmdd yyyymmdd {cat_id}
```

Note:

* The object that the user is trying to call this cmd on must exists or the cmd will throw an error.
* If the user does not follow the range format as show above, the cmd will not work properly.

## 

<h2 id='specific_change'>Specific Changes</h2>

<h3 id='cat_fam'>Category Family</h3>

* Not Applicable.

<h3 id='org_fam'>Organization Family</h3>

* Added the delete option for 'AddPart' in order to amend mistakes.
* In order to reduce the footprint on leaf nodes, "pt_list' only stores the uuid of the designated Part.

###### AddPart

allows the user to establish relationship between Organization and Part.

```bash
    $ organization AddPart {org_id} {pt_id} {pri_key} {pub_key}
```

Note:

* Part must exists for this cmd to run successfully.
* The cmd will fail if there exists exact Part in Organization.

###### AddPart --delete

allows the user to sever the established relationship between Organization and Part. (Mainly to amend mistakes).

```bash
    $ organization AddPart --delete {org_id} {pt_id} {pri_key} {pub_key}
```

Note:

* In order to amend mistakes, the user must first call the delete option and then invoke the 'Add' function again.
* For Organization to successfully call this cmd, the Part has to exists in the Organization.

<h3 id='pt_fam'>Part Family</h3>

* Added the delete option for all the 'Add' functions in order to amend mistakes.
* In order to reduce the footprint on leaf nodes, respective list only stores the uuid of the designated Artifact, Category, or Supplier (Organization).

###### AddArtifact

allows the user to establish relationship between Part and Artifact.

```bash
    $ pt AddArtifact {pt_id} {art_id} {pri_key} {pub_key}
```

Note:

* Artifact must exists for this cmd to run successfully.
* The cmd will fail if there exists exact Artifact in Part.

###### AddArtifact --delete

allows the user to sever the established relationship between Part and Artifact.

```bash
    $ pt AddArtifact --delete {pt_id} {art_id} {pri_key} {pub_key}
```

Note:

* In order to amend mistakes, the user must first call the delete option and then invoke the 'Add' function again.
* For Part to successfully call this cmd, the Artifact has to exists in the Part. 

###### AddCategory

allows the user to establish relationship between Part and Category.

```bash
    $ pt AddCategory {pt_id} {cat_id} {pri_key} {pub_key}
```

Note:

* Category must exists for this cmd to run successfully.
* The cmd will fail if there exists exact Category uuid in Part.

###### AddCategory --delete

allows the user to sever the established relationship between Part and Category.

```bash
    $ pt AddCategory --delete {pt_id} {cat_id} {pri_key} {pub_key}
```

Note:

* In order to amend mistakes, the user must first call the delete option and then invoke the 'Add' function again.
* For Part to successfully call this cmd, the Category has to exists in the Part.

###### AddSupplier

allows the user to establish relationship between Part and Organization.

```bash
    $ pt AddSupplier {pt_id} {org_id} {pri_key} {pub_key}
```

Note:

* Organization must exists for this cmd to run successfully.
* The cmd will fail if there exists exact Organization uuid in Part.

###### AddSupplier --delete

allows the user to sever established relationship between Part and Organization.

```bash
    $ pt AddSupplier --delete {pt_id} {org_id} {pri_key} {pub_key}
```

Note:

* In order to amend mistakes, the user must first call the delete option and then invoke the 'Add' function again.
* For Part to successfully call this cmd, the Organization has to exists in the Part.

<h3 id='art_fam'>Artifact Family</h3>

* Added the delete option for all the 'Add' functions in order to amend mistakes.

###### AddArtifact

allows the user to establish relationship between Artifact and Sub-Artifact.

```bash
    $ artifact AddArtifact {art_id} {sub_art_id} {path} {pri_key} {pub_key}
```

Note:

* Sub-Artifact (Artifact which the user is trying add) must exists for this cmd to run successfully.
* Identical Sub-Artifact cannot be added.

###### AddArtifact --delete

allows the user to sever the established relationship between Artifact and Sub-Artifact.

```bash
    $ artifact AddArtifact --delete {art_id} {sub_art_id} {path} {pri_key} {pub_key}
```

Note:

* In order to amend mistakes, the user must first call the delete option and then invoke the 'Add' function again.
* For Artifact to successfully call this cmd, the Sub-Artifact and its path must be identical to the one stored in Artifact.

###### AddURI

allows the user to establish relationship between Artifact and URI.

```bash
    $ artifact AddURI {art_id} {uri_version} {uri_checksum} {uri_content_type} {uri_size} {uri_type} {location} {pri_key} {pub_key}
```

Note:

* Identical URI cannot be added.

###### AddURI --delete

allows the user to sever the established relationship between Artifact and URI.

```bash
    $ artifact AddURI --delete {art_id} {uri_version} {uri_checksum} {uri_content_type} {uri_size} {uri_type} {location} {pri_key} {pub_key}
```

Note:

* In order to amend mistakes, the user must first call the delete option and then invoke the 'Add' function again.
* For Artifact to successfully call this cmd, the URI and all of its dependencies must be identical to the one stored in Artifact.
