# Algorig

Algorig is a very compact cli tool which tries to ease your Algorand Stateful Smart Contracts development and tooling processes while still providing you all the flexibility. It simply utilizes PyTeal and Algorand Python SDK to ensure the smart contract development feels quite native and fluent.

## Disclaimer
This project is in very early stages and not ready for practical use yet.

## Setup / Installation

### Setting up Algorand Sandbox
Before we get started, we'll need an Algorand Node and KMD services up and running preferably in local environment to able interact with Algorand blockchain and manage our accounts. 

The shortest way to run an Algorand node and KMD indexing services for development purposes is installing a sandboxed Algorand node locally. To accomplish this, simply checkout and run the Algorand Sandbox repository by typing the commands below.

```bash
$ git clone https://github.com/algorand/sandbox.git
$ cd sandbox
$ ./sanbox up
```

Once ready, you will have a full Algod and KMD services running locally under `Release` configuration which is a private network suitable for local development.

Here, before starting our smart contract development, we'll need a contract owner account which will own the smart contract we develop on Algorand blockchain. Thanlfully Algorand Sandbox default configuration comes with a default preconfigured wallet named `unencrypted-default-wallet` containing a couple of accounts those already has a significant Algo balance which is very good enough to start with.

```bash
$ ./sandbox goal wallet list
##################################################
Wallet: unencrypted-default-wallet (default)
ID: de87213c0d084688bb4e40fe2045e16a
##################################################
```

You can also list your predefined account comes with

```bash
$ ./sandbox goal account list -w unencrypted-default-wallet
[online]  DNSNRCJ6WO4LCVNE6O6JHYSZQ7C725RVJMMTT4GCBOUH4VPMPMZYUVBFLU  DNSNRCJ6WO4LCVNE6O6JHYSZQ7C725RVJMMTT4GCBOUH4VPMPMZYUVBFLU  4000008000000000 microAlgos
[offline] DRE4XUEJBPVHHFIUWT5SGH3JIGS5RDUBWYXASA72PINNUVFJIY6SFKSLEE  DRE4XUEJBPVHHFIUWT5SGH3JIGS5RDUBWYXASA72PINNUVFJIY6SFKSLEE  1000002000000000 microAlgos
[offline] HPAMDTCS3B2BZUGP5JUNDNBKVWXYPKPC56VEYT3WYBEONPVD6HJLUHMTVQ  HPAMDTCS3B2BZUGP5JUNDNBKVWXYPKPC56VEYT3WYBEONPVD6HJLUHMTVQ  4000008000000000 microAlgos
```

Now feel free to pick one of the accounts as the contract owner so that we can proceed to our Algorig setup. Please refer the Algorand Sandbox project page itself for more configuration options and any other details.

### Get started with Algorig

Since we're done with our local Algorand Node setup, now we're ready to develop an Algorand smart sontract using Algorig. Before we start, let's first configure a virtual environment located under a project directory which will be the home folder of our smart contract project.

```bash
$ mkdir mydefi
$ cd mydefi
$ python -m venv venv
$ source venv/bin/activate
```

 Once your virtual environment is up and ready, you may now install the Algorig itself. The best way to install Algorig is simply using pip command as shown below:

```bash
$ pip install algorig
```

At this point, since you put your tool belt on, you're ready initialize a fresh new Algorig work bench by typing the command below.

```bash
$ rig init --signing-address DNSNRCJ6WO4LCVNE6O6JHYSZQ7C725RVJMMTT4GCBOUH4VPMPMZYUVBFLU
```

This command will create two things. The first one is the main configuration file which you will be able to configure your smart contract development environment.

```bash
$ cat .rig.rc
[DEFAULT]
algod_address = http://localhost:4001
algod_token = aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa
kmd_address = http://localhost:4002
kmd_token = aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa
wallet_name = unencrypted-default-wallet
wallet_password =
signing_address = DNSNRCJ6WO4LCVNE6O6JHYSZQ7C725RVJMMTT4GCBOUH4VPMPMZYUVBFLU
app_module = protocol
teal_version = 4
num_global_byte_slices = 0
num_global_ints = 0
num_local_byte_slices = 0
num_local_ints = 0
```

Here you might have noticed that how we used the contract owner account address by utilizing the `--signing-address` parameter. Likewise the use of such cli parameters will help us overriding above the default configuration values those mostly aleady supposed to conform the default settings of our Algorand Sandbox setup mentioned above.

Furthermore, `init` command also proposes a stub python module called `protocol.py` which contains the main entry point to your smart contract. It's simply a class declaration with a special name `Application` which also inherits and implements a base class `BaseApplication` comes with Algorig module itself.

```python
$ cat protocol.py
from pyteal import *

from algorig.application import BaseApplication

class Application(BaseApplication):

    def get_approval_program(self):
        # Implement your contract here using pyteal
        return Int(0)

    def op_example_command(self, example_param):
        # This is an example contract call op which can be used as cli command
        print('Hello ', example_param)
```

You may notice that `Application` class simply proposes a method called `get_approval_program` of which you're expected to implement your main smart contract logic under this method.

Also you might have noticed the `op_example_command` method starting with a special prefix `op`. Algorig simply translates these special named class methods into cli commands which can be directly used to manage your smart contract operations those are supposed to communicate with on your smart contracts.

To see the available commands, simple type `rig` or `rig --help`

```bash
$ rig --help
sage: rig [-h] [-v] {init,application_create,application_update,example_command} ...

positional arguments:
  {init,application_create,application_update,example_command}

optional arguments:
  -h, --help            show this help message and exit
  -v, --version         show program's version number and exit
```

You'll notice the `example_command` ready to be typed at your finger tips. Just type the command to see the expected output.

```bash
$ rig example_command myparam123
Hello myparam123
```

While this command does nothing rather than simply printing into console, such commands are generally supposed to perform some operations with your implemented smart contract by presumably utilizing `ApplicationCall` or any other available application transactions calls which we'll see later on.

### Write and deploy your first contract

As mentioned previously, `get_approval_program()` method is the main entry point for your Algorand smart contract. You're here simply expected to return your PyTeal node object and Algorig will do the rest for you.

Let's write a very simple contract which only accepts application create and update transactions respectively.

```python

def get_approval_program(self):
    # Implement your contract here using pyteal

    return Cond(
        [Txn.application_id() == Int(0), Int(1)],
        [Txn.on_completion() == OnComplete.UpdateApplication, Int(1)],
    )
```

Congrats, you just implemented your first Algorand smart contract. At this point, since you'll need to deploy your contract to Algorand blockchain, Algorig here will help us to deploy it with a built-in command `application_create` by performing some magic behind in order to save us writing so many boilerplate code to achive the same.

Let's find out how the command works at first.

```bash
$ rig application_create --help
usage: rig application_create [-h] [--app_args APP_ARGS]

optional arguments:
  -h, --help           show this help message and exit
  --app_args APP_ARG
```

It not seems to be fine and legit using the command directly without any parameteres in our case.

Let's run the command.

```bash
$ rig create_application
Processing transaction: A35EASTS6ANOO5HTAFIWZAAPSWJJ653ZFM74APMHE46ZIKXDNQDQ
........
Confirmed at round: 2342525
Application created with id: 1
```

Success! This built-in command essentially compiled your teal code, created an `ApplicationCreate` transaction  automatically and sent it to Algorand blockchain throughout the Algod service by referring the `algod_address` and `algod_token` settings located in your config file. In our case, those settings have already the default values referring the sandbox Algod service we just started locally.

```bash
# .rig.rc
...
algod_address = http://localhost:4001
algod_token = aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa
...
```

Another side effeect of this commmand is that whenever our application initially created on the blockchain this command will save and keep the id of the application just created in our config file using the key `app_id`. At this point if you dump the contents of our config file,  you'll see the `app_id` setting which was absent previously.

```bash
# .rig.rc
...
app_id = 1
...
```

This setting will basically help Algorig to able to locate your application any time you want to interact with later on. For example there is another built-in command called `application_update` which uses this setting to locate the application. So now it's a good time to also see how to deploy any changes in the contract.

Let's change a bit of our contract, this time let our contract to accept an `ApplicationCall` transaction to perform some tasks on the contract. In this case, it will simply expect a sigle arg `"Hello World"` to approve the transaction.

```python

def get_approval_program(self):
    # Implement your contract here using pyteal

    def on_call():
        return Txn.application_args[0] == Bytes('Hello World')

    return Cond(
        [Txn.application_id() == Int(0), Int(1)],
        [Txn.on_completion() == OnComplete.UpdateApplication, Int(1)],
        [Txn.on_completion() == OnComplete.NoOp, on_call()],
    )
```

Now you should be able to send your updates to your contract contract using the command below:

```bash
$ python application_update
Processing transaction: H3ZBGVX4SVPAPHPZT23Q3LHIMTOQBEY2H6SDHGARCABLWRB7JNLA
......
Confirmed at round: 5493
Application updated successfully.
```

Congratulations, you just developed and deployed your first smart contract to Alogrand blockchain.

### Interact with our Smart Contract

TODO:


---
More documentation coming soon with further improvements.