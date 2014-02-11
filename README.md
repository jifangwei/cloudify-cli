# cosmo-cli

Command line interface for [Cloudify](https://github.com/CloudifySource/cosmo-manager)

* [Deploying your first application - Walkthrough](#deploying-your-first-application---walkthrough)
* [Providers](#providers)
  * [Currently Supported Providers](#currently-supported-providers)
  * [Creating a new provider extension](#creating-a-new-provider-extension)
* [Working-Directory Settings and Configurations](#working-directory-settings-and-configurations)
* [Commands Docs](#commands-docs)


---


## Deploying your first application - Walkthrough
**1. Installing the CLI and a provider extension:**
  - Install Cloudify CLI (temporary url, will be on PyPI soon):  
  `pip install https://github.com/CloudifySource/cosmo-cli/archive/develop.zip`  
  (Note: if you're using Pip 1.5 or above, add the "*--process-dependency-links*" flag to the 'pip install' command)  

  - Install a Cloudify provider extension (Openstack is used in this example):
  `apt-get install python-dev # or the equivalent *nix version of this command`
  `pip install https://github.com/CloudifySource/cloudify-openstack/archive/develop.zip`

<br>
**2. Initializing:**
  - Cd into your favorite working directory and initialize Cloudify for some provider:  
  `cfy init openstack`

  - Edit the autogenerated provider-specific config file "*cloudify-config.yaml*" - update its mandatory (non-commented) settings as needed.  
    (For more information about the configuration files parameters used in this example, view the [Cloudify-Openstack readme](https://github.com/CloudifySource/cloudify-openstack/blob/develop/README.md))

  - Bootstrap cloudify on Openstack:  
  `cfy bootstrap`  
  This could take a bit of time to finish... Looking for something to do in the meanwhile? http://dynamic.xkcd.com/random/comic/

<br>
**3. Deploying your application:**
  - Upload your blueprint:  
  `cfy blueprints upload my-app/blueprint.yaml -a my-blueprint`  
  (Don't have a blueprint? You can download a sample one [here](https://github.com/CloudifySource/cloudify-hello-world/tree/develop/openstack)).

  - Create a deployment of the blueprint:  
  `cfy deployments create my-blueprint -a my-deployment`

  - Execute an install operation on the deployment:  
  `cfy deployments execute install my-deployment`

This will install your deployment - all you have left to do is sit back and watch the events flow by until the deployment is complete.

<br>
**4. Fetching execution events:**
  - List deployment executions:
  `cfy executions list my-deployment`

  - Fetch execution events by execution id:
  `cfy events --execution-id f6269ccf-1243-439e-b779-c0f8d06a9894`


---


## Providers
A provider is any platform which allows for the creation and bootstrapping of a management server (e.g. Openstack). The CLI can work with any provider once the appropriate extension has been installed. A provider extension is provider-specific code which handles environment-related operations such as bootstrap and teardown.

Note that the CLI can be used even without the installation of any providers - if you already possess a bootstrapped management server, you may simply direct the CLI to work with that server (`cfy use <management-ip>`), and you can then issue any of the CLI commands to that server (with the exception of the "**cfy teardown**" command)


###Currently Supported Providers:
* [Openstack](https://github.com/CloudifySource/cloudify-openstack/tree/develop)
* [Vagrant](https://github.com/CloudifySource/cloudify-vagrant/tree/develop)


### Creating a new provider extension:
Provider extensions are simply Python modules which adhere to certain conventions and implement a certain interface.  

By convention, the module name is called "*cloudify_<provider-name>.py*". While any name is viable in practice, the CLI **cfy init** command, which receives a '*provider*' parameter, is set to first search for a module named by the convention, and only search for the exact '*provider*' value given if such a module was not found.

Every provider extention is expected to implement the following interface:

  - **init**(*target_directory*, *reset_config*, *is_verbose_output=False*)  
    - **Description**: This method is used to create any required configuration files at the given target directory, as well as make any other initializations required by the specific provider.  
    - **Parameters:**:
      - *target_directory* - Target directory for configuration files, if any.
      - *reset_config* - A boolean describing whether overwriting existing configuration files is allowed.
      - *is_verbose_output* - A flag for setting verbose output
    - **Returns:**: False if a configuration file already exists and reset_config is False; True otherwise.
  
  - **bootstrap**(*config_file_path=None*, *is_verbose_output=False*)  
    - **Description**: This method is used to set up the management server as well as the environment (e.g. network) in which it resides. It is currently also responsible for bootstrapping the server as a management server.  
    - **Parameters**:
      - *config_file_path=None* - A path to an appropriate configuration file to be used in the bootstrap process. If one is required yet not passed, the Provider is expected to assume this command is called from the same path from which "init" was called, and search for the relevant file in the current directory.
      - *is_verbose_output* - A flag for setting verbose output
    - **Returns**: The IP of the bootstrapped management server.
  
  - **teardown**(*management_ip*, *is_verbose_output=False*)  
    - **Description**: This method is used to tear down the server at the address supplied, as well as any environment objects related to the server which will no longer be of use.
    - **Parameters**:
      - *management_ip* - The IP of the management server to teardown.
      - *is_verbose_output* - A flag for setting verbose output
    - **Returns**: None.  


Another convention worth mentioning is one used for the Provider's **init** method: While a Provider may create any number of provider-specific configuration files on init (or none at all) in any format it so chooses, the standard is for it to create a single configuration file in YAML format named "*cloudify-config.yaml*". Additionally, it's recommended that all default values in the file are commented out, for ease of use. 

---


## Working-Directory Settings and Configurations

When running the CLI **cfy init** command, a "*.cloudify*" file will be created in the target directory. All local settings (such as the default management server and aliases) are stored in that file, and only take effect when using the CLI from the target directory.

Additionally to creating the "*.cloudify*" file, the **cfy init** command will usually also create a provider-specific configuration file named "*cloudify-config.yaml*", which will later be used by the **cfy bootstrap** command. This, however, is merely a convention, one which various providers may choose not to follow.

Note: If the Cloudify working directory is also a git repository, it's recommended to add "*.cloudify*" to the .gitignore file.


-----


## Commands Docs
re
**Command:** status

**Description:** queries the status of the management server

**Usage:** `cfy status [-t, --management-ip <ip>] [-v, --verbosity]`

**Parameters**:

- management-ip: the management-server to use (Optional)
- is_verbose_output - A flag for setting verbose output (Optional)

**Example:** `cfy status`

------
  
**Command:** use

**Description:** defines a default management server to work with

**Usage:** `cfy use <management_ip> [-a, --alias <alias>] [-f, --force] [-v, --verbosity]`

**Parameters**:

- management_ip: the management-server to define as the default management server
- alias: a local alias for the given management server address (Optional)
- force: a flag indicating authorization to overwrite the alias provided if it's already in use (Optional)
- is_verbose_output - A flag for setting verbose output (Optional)

**Example:** `cfy use 10.0.0.1 -a my-mgmt-server`
  
------
  
**Command:** init

**Description:** initializes a cloudify working directory for a given provider

**Usage:** `cfy init <provider> [-t, --target-dir <dir>] [-r, --reset-config] [-v, --verbosity]`

**Parameters**:

- provider: the cloudify provider to use for initialization
- target-dir: the directory that will be used as the cloudify working directory (Optional)
- reset-config: a flag indicating overwriting existing configuration is allowed (Optional)
- is_verbose_output - A flag for setting verbose output (Optional)

**Example:** `cfy init openstack`
  
------
  
**Command:** bootstrap

**Description:** bootstraps cloudify on the current provider

**Usage:** `cfy bootstrap [-c, --config-file <file>] [-v, --verbosity]`

**Parameters**:

- config-file: path to the config file (Optional)
- is_verbose_output - A flag for setting verbose output (Optional)

**Example:** `cfy bootstrap`
  
------
  
**Command:** teardown

**Description:** tears down the management-server, as well as any local aliases under its context

**Usage:** `cfy teardown [-f, --force] [-t, --management-ip <ip>] [-v, --verbosity]`

**Parameters**:

- force: a flag indicating confirmation for this irreversable action (Optional)
- management-ip: the management-server to use (Optional)
- is_verbose_output - A flag for setting verbose output (Optional)

**Example:** `cfy teardown -f`
  
------
  
**Command:** blueprints upload

**Description:** uploads a blueprint to the management server
  
**Usage:** `cfy blueprints upload <blueprint_path> [-a, --alias <alias>] [-t, --management-ip <ip>] [-v, --verbosity]`

**Parameters**:

- blueprint_path: path to the blueprint (yaml file) to upload
- alias: a local alias for the blueprint id that will be created for the uploaded blueprint (Optional)
- management-ip: the management-server to use (Optional)
- is_verbose_output - A flag for setting verbose output (Optional)

**Example:** `cfy blueprints upload blueprint.yaml -a my-blueprint`
  
------
  
**Command:** blueprints list

**Description:** lists the blueprint on the management server, as well as the blueprints local aliases
  
**Usage:** `cfy blueprints list [-t, --management-ip <ip>] [-v, --verbosity]`

**Parameters**:

- management-ip: the management-server to use (Optional)
- is_verbose_output - A flag for setting verbose output (Optional)

**Example:** `cfy blueprints list`
  
------
  
**Command:** blueprints delete

**Description:** deletes the blueprint from the management server
  
**Usage:** `cfy blueprints delete <blueprint_id> [-t, --management-ip <ip>] [-v, --verbosity]`

**Parameters**:

- blueprint_id: the id or alias of the blueprint to delete
- management-ip: the management-server to use (Optional)
- is_verbose_output - A flag for setting verbose output (Optional)

**Example:** `cfy blueprints delete my-blueprint`
  
------
  
**Command:** blueprints alias

**Description:** creates a local alias for a blueprint id
  
**Usage:** `cfy blueprints alias <alias> <blueprint_id> [-f, --force] [-t, --management-ip <ip>] [-v, --verbosity]`

**Parameters**:

- alias: the alias for the blueprint id
- blueprint_id: the id of the blueprint
- force: a flag indicating authorization to overwrite the alias provided if it's already in use (Optional)
- management-ip: the management-server to use (Optional)
- is_verbose_output - A flag for setting verbose output (Optional)

**Example:** `cfy blueprints alias my-blueprint 38f8520f-809f-4162-ae96-75555d906faa`

------
  
**Command:** deployments create

**Description:** creates a deployment of a blueprint
  
**Usage:** `cfy deployments create <blueprint_id> [-a, --alias <alias>] [-t, --management-ip <ip>] [-v, --verbosity]`

**Parameters**:

- blueprint_id: the id or alias of the blueprint to deploy
- alias: a local alias for the deployment id that will be created for the new deployment (Optional)
- management-ip: the management-server to use (Optional)
- is_verbose_output - A flag for setting verbose output (Optional)

**Example:** `cfy deployments create my-blueprint -a my-deployment`  

------
  
**Command:** deployments execute

**Description:** executes an operation on a deployment
  
**Usage:** `cfy deployments execute <operation> <deployment_id> [-t, --management-ip <ip>] [-v, --verbosity]`

**Parameters**:

- operation: the name of the operation to execute
- deployment_id: the deployment id or alias on which the operation should be executed
- management-ip: the management-server to use (Optional)
- is_verbose_output - A flag for setting verbose output (Optional)

**Example:** `cfy deployments execute install my-deployment`
  
------
  
**Command:** deployments alias

**Description:** creates a local alias for a deployment id
  
**Usage:** `cfy deployments alias <alias> <deployment_id> [-f, --force] [-t, --management-ip <ip>] [-v, --verbosity]`

**Parameters**:

- alias: the alias for the deployment id
- deployment_id: the id of the deployment
- force: a flag indicating authorization to overwrite the alias provided if it's already in use (Optional)
- management-ip: the management-server to use (Optional)
- is_verbose_output - A flag for setting verbose output (Optional)

**Example:** `cfy deployments alias my-deployment 38f8520f-809f-4162-ae96-75555d906faa`  

------

**Command** deployments list

**Description** Lists deployments on management server

**Usage** `cfy deployments list [-b, --blueprint-id <blueprint-id>] [-t, --management-ip <ip>] [-v, --verbosity]`

**Parameters**:
- blueprint-id: the id or alias of the blueprint to to list deployments for (Optional, lists all deployments if not provided)
- management-ip: the management-server to use (Optional)
- is_verbose_output - A flag for setting verbose output (Optional)

------
  
**Command:** workflows list

**Description:** lists the workflows of a deployment
  
**Usage:** `cfy workflows list <deployment_id> [-t, --management-ip <ip>] [-v, --verbosity]`

**Parameters**:

- deployment_id: the alias or id of the deployment whose workflows to list
- management-ip: the management-server to use (Optional)
- is_verbose_output - A flag for setting verbose output (Optional)

**Example:** `cfy workflows list my-deployment`  


------

**Command:** executions list

**Description:** lists the executions of a deployment

**Usage:** `cfy executions list <deployment_id> [-t, --management-ip <ip>] [-v, --verbosity]`

**Parameters**:

- deployment_id: the id of the deployment whose executions to list
- management-ip: the management-server to use (Optional)
- is_verbose_output - A flag for setting verbose output (Optional)

**Example:** `cfy executions list my-deployment`


------

**Command:** events

**Description:** fetches events of an execution

**Usage:** `cfy events [-h] [-e EXECUTION_ID] [-l, --include-logs] [-t, --management-ip <ip>] [-v, --verbosity]`

**Parameters**:

- execution-id: the id of the execution to fetch events for
- include-logs: determines whether to fetch logs in addition to events
- management-ip: the management-server to use (Optional)
- is_verbose_output - A flag for setting verbose output (Optional)

**Example:** `cfy events --execution-id 92515e66-5c8f-41e0-a361-2a1ad92706b2`
