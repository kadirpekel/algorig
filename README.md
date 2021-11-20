# Algorig

Algorig is a very compact cli tool which tries to ease your Algorand Stateful Smart Contracts development and tooling processes while still providing you all the flexibility. It simply utilizes PyTeal and Algorand Python SDK to ensure the smart contract development feels quite native and fluent.

## Disclaimer
This project is in very early stages and not ready for practical use yet.

## Setup / Installation
Most cases you'd rather work in a virtual python environment.
```
$ mkdir mydefi
$ cd mydefi
$ python -m venv venv
$ source venv/bin/activate
```
Once your virtual environment is ready,  you may now install the Algorig. The best way to install Algorig is using pypi repositories via `easy_install` or `pip`:

```
$ pip install algorig
```

At this point, since you put your tool belt, you're ready initialize a fresh new Algorig work bench by typing the command below. 

```
$ rig init
```
This command will create two things. The first one is the main configuration file which you will be able to configure your smart contract development environment.

```
$ cat .rig.rc
[DEFAULT]
algod_address = http://localhost:4001
algod_token = aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa
kmd_address = http://localhost:4002
kmd_token = aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa
wallet_name = unencrypted-default-wallet
wallet_password =
signing_address = aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa
app_module = protocol
teal_version = 4
num_global_byte_slices = 0
num_global_ints = 0
num_local_byte_slices = 0
num_local_ints = 0
```

`init` command also proposes a stub python module called `protocol.py` which contains main entry point to your smart contract. It's simply a class declaration with a special name `Application` which also inherits and implements a base class `BaseApplication` which comes with Algorig module itself.

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

Also you may have noticed the `op_example_command` method starting with a special prefix `op`. Algorig simply translates these special named class methods into cli commands which can be directly used to manage your operations those are supposed to communicate with on your smart contracts.

To see the available commands, simple type `rig` or `rig --help`
```
$ rig --help
sage: rig [-h] [-v] {init,application_create,application_update,example_command} ...

positional arguments:
  {init,application_create,application_update,example_command}

optional arguments:
  -h, --help            show this help message and exit
  -v, --version         show program's version number and exit
```

You'll notice the `example_command` ready to be type at your finger tips. Just type the command to see the output.

```
$ rig example_command myparam123
Hello myparam123
```

While this command does nothing rather than simply printing into console, these commands are generally supposed to contact with your implemented smart contract by mostly utilizing `ApplicationCall` transaction calls. With this idea in mind, you may use such functionality to interact with your smart contract using cli commands easily.

```python
def op_setup(self, example_arg):
    return self.submit([
        ApplicationCallTxn(
            sender=self.config['signing_address'],
            index=self.config['app_id'],
            on_complete=transaction.OnComplete.NoOpOC,
            app_args=[b"setup", example_arg],
            sp=self.algod.suggested_params(),
        )
    ])
```

This example will show us how easily you can send an application call transaction `setup` to your deployed contract by typing the command below:

```
$ rig setup "my example arg"
Processing transaction: A35EASTS6ANOO5HTAFIWZAAPSWJJ653ZFM74APMHE46ZIKXDNQDQ
........
Confirmed at round: 2342525
```

---
More documentation coming soon with further improvements.