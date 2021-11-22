```

 _______  ___      _______  _______  ______    ___   _______ 
|   _   ||   |    |       ||       ||    _ |  |   | |       |
|  |_|  ||   |    |    ___||   _   ||   | ||  |   | |    ___|
|       ||   |    |   | __ |  | |  ||   |_||_ |   | |   | __ 
|       ||   |___ |   ||  ||  |_|  ||    __  ||   | |   ||  |
|   _   ||       ||   |_| ||       ||   |  | ||   | |   |_| |
|__| |__||_______||_______||_______||___|  |_||___| |_______|

```

# Welcome to Algorig - The Ultimate Algorand Smart Contract Development Rig!

Algorig is a very compact and intuitive cli tool which tries to ease your Algorand smart contract development and tooling while still preserving all the flexibility. It simply utilizes PyTeal and Algorand Python SDK to make sure that your smart contract development feels quite native and fluent.

## Setup / Installation

### Setting up Algorand Sandbox
Before we get started, we'll need an Algorand Node containing the Algod and KMD services up and running preferably in local environment to be able to interact with Algorand blockchain and manage our accounts.

The shortest way to run an Algorand node for development purposes is installing Algorand sandbox locally. To accomplish this, simply checkout the Algorand sandbox repository and run it by typing the commands below.

```bash
$ git clone https://github.com/algorand/sandbox.git
$ cd sandbox
$ ./sanbox up
```

Once the sandbox up and ready, you will have the both Algod and KMD services running locally under `Release` configuration which is a private network suitable for local development.

Here, before getting started to our smart contract development, we'll need a Algorand account that will own the smart contract we develop on the Algorand blockchain. Thankfully, the Algorand sandbox default configuration comes with a default wallet named `unencrypted-default-wallet` also containing a couple of accounts those already has a significant $algo balance which is quite sufficient enough to start with.

```bash
$ ./sandbox goal wallet list
##################################################
Wallet: unencrypted-default-wallet (default)
ID: de87213c0d084688bb4e40fe2045e16a
##################################################
```

You can also list all the accounts under the default wallet comes with your sandbox installation.

```bash
$ ./sandbox goal account list -w unencrypted-default-wallet
[online]  DNSNRCJ6WO4LCVNE6O6JHYSZQ7C725RVJMMTT4GCBOUH4VPMPMZYUVBFLU  DNSNRCJ6WO4LCVNE6O6JHYSZQ7C725RVJMMTT4GCBOUH4VPMPMZYUVBFLU  4000008000000000 microAlgos
[offline] DRE4XUEJBPVHHFIUWT5SGH3JIGS5RDUBWYXASA72PINNUVFJIY6SFKSLEE  DRE4XUEJBPVHHFIUWT5SGH3JIGS5RDUBWYXASA72PINNUVFJIY6SFKSLEE  1000002000000000 microAlgos
[offline] HPAMDTCS3B2BZUGP5JUNDNBKVWXYPKPC56VEYT3WYBEONPVD6HJLUHMTVQ  HPAMDTCS3B2BZUGP5JUNDNBKVWXYPKPC56VEYT3WYBEONPVD6HJLUHMTVQ  4000008000000000 microAlgos
```

Please refer the Algorand sandbox project page itself for more configuration options and any other details.

Now feel free to pick one of the accounts listed above as a contract owner so that we can assign it while setting up our Algorig project.

### Get started with Algorig

Since we're done with our local Algorand node setup, now we're ready to develop an Algorand smart sontract using Algorig. Before we start, let's first configure a virtual environment located under a project directory which will be the home folder of our smart contract project.

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

At this point, since you put your tool belt on, you're ready initialize a fresh new Algorig project by typing the command below.

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

Here, you might have also noticed how we used the contract owner account address by utilizing the `--signing-address` parameter. Likewise, the use of such cli parameters will help us overriding the default configuration values above those mostly supposed to conform the default settings of our Algorand sandbox setup done before.

Furthermore, `init` command also proposes a stub python module called `protocol.py` which contains the main entry point to your smart contract development. It's simply a class declaration with a special name `Application` which also inherits and implements a base class `BaseApplication` comes with Algorig module itself.

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

You may notice that `Application` class simply proposes a method called `get_approval_program()` the one you're expected to implement your main smart contract logic under it.

Also you might have noticed the `op_example_command` method starting with a special prefix `op`. Algorig simply translates these special named class methods into cli commands which can be directly used to manage your smart contract operations those are supposed to interact with your smart contracts.

To see all the available commands, simple type `rig` or `rig --help`

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

While this command does nothing rather than simply printing into console, such commands are generally supposed to perform some operations with your deployed smart contract by presumably utilizing `ApplicationCall` or any other available transactions calls which we'll see later on.

### Write and deploy your first contract

As mentioned previously, `get_approval_program()` method is the main entry point to your Algorand smart contract. You're here simply expected to return a PyTeal node object and Algorig will handle the rest for you.

Ok, let's write a very simple contract which only accepts application create and update transactions respectively.

```python

def get_approval_program(self):
    # Implement your contract here using pyteal

    return Cond(
        [Txn.application_id() == Int(0), Int(1)],
        [Txn.on_completion() == OnComplete.UpdateApplication, Int(1)],
    )
```

Congrats, you just implemented your first Algorand smart contract. At this point, since you'll need to deploy your contract to Algorand blockchain, Algorig here will help us to deploy it with a built-in command `application_create` by performing some magic behind in order to save us writing so many boilerplate code to achive the same.

First of all, let's find out how the command works before acutally running it.

```bash
$ rig application_create --help
usage: rig application_create [-h] [--app_args APP_ARGS]

optional arguments:
  -h, --help           show this help message and exit
  --app_args APP_ARG
```

It seems to be legit using the command directly without any given parameteres in our case.

Let's run the command.

```bash
$ rig create_application
Processing transaction: A35EASTS6ANOO5HTAFIWZAAPSWJJ653ZFM74APMHE46ZIKXDNQDQ
........
Confirmed at round: 2342525
Application created with id: 1
```

Success! This built-in command essentially compiled your teal code, created an application create transaction automatically and sent it to Algorand blockchain throughout the Algod service by referring the `algod_address` and `algod_token` settings located under our config file. In our case, those settings have already the default values referring the sandbox Algod service we just started locally.

```bash
# .rig.rc
...
algod_address = http://localhost:4001
algod_token = aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa
...
```

Another side effect of this commmand is that whenever our application initially created on the blockchain, this command will save and keep the `id` of our application under our config file using the configuration key of `app_id`. At this point, if you dump the contents of our config file,  you'll notice the `app_id` setting which was absent previously.

```bash
# .rig.rc
...
app_id = 1
...
```

This setting will basically help Algorig to locate your application whenever you want to interact with it. For example, there is also another built-in command called `application_update` which uses this setting while locating your application created previously.

So now, it's a good time to also see how to deploy any changes in the contract.

Ok, let's change a bit of our contract. This time let our contract to accept an `ApplicationCall` transaction to perform some tasks on the contract. In our case, it will simply expect a sigle arg `"Hello World"` to approve the transaction.

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

Now you should be able to send your updates and override your existing contract using the command below:

```bash
$ python application_update
Processing transaction: H3ZBGVX4SVPAPHPZT23Q3LHIMTOQBEY2H6SDHGARCABLWRB7JNLA
......
Confirmed at round: 5493
Application updated successfully.
```

Congratulations, you just developed, deployed and also updated your first smart contract to Alogrand blockchain.

### Interact with our Smart Contract

So far, we've already seen how Algorig smoothens our Algorand smart contract development with some smart tooling methods. We already created our first smart contract and updated it by using the built-in commands. This time, let's now assume that we need to interact with our contract with a purpose. By our last update, our contract now expects us to send an application call transaction with a single parameter with the value of `"Hello World`.

So let's try to implement such a command together to see how to develop and perform the contract operations.

```python

from algosdk.future import transaction

class Application(BaseApplication):

  ...

  def op_hello_world(self, my_param):
    self.submit(transaction.ApplicationCallTxn(
        sp=self.algod.suggested_params(),
        on_complete=transaction.OnComplete.NoOpOC,
        index=self.config.getint('app_id'),
        sender=self.config['signing_address'],
        app_args=[bytes(my_param, 'ascii')],
    ))

```

That's simple as it. We just implemented a `hello_world` command to interact with our contract. Let's first locate it.

```bash
$ rig --help
usage: rig [-h] [-v] {init,application_create,application_update,hello_world} ...

positional arguments:
  {init,application_create,application_update,hello_world}

optional arguments:
  -h, --help            show this help message and exit
  -v, --version         show program's version number and exit

```

Also you may check the further details about our new command by seeing the helper instructions of the command itself.

```bash
$ rig hello_world --help
usage: rig hello_world [-h] my_param

positional arguments:
  my_param

optional arguments:
  -h, --help  show this help message and exit
```

Since the `hello_world` command ready at your fingertips, just run it to see if it works as expected.

```bash
$ rig hello_world "Hello World"
Processing transaction: LBF5NQOM2WWIZ4ZUPAVTPKXTK7MD5TODPW2JO65UGNSASQ4IZT2Q
........
Confirmed at round: 6054
```

Perfect! You just interacted with your contract deployed on the blockchain. Now let's see what happens when we send a different parameter to our contract.


```bash
$ rig hello_world "No Way"
algosdk.error.AlgodHTTPError: TransactionPool.Remember: transaction 4GFYWBASWI7T5GERJKO5R4GUUXUDH4LQGCO55BVUKJNXNCQQAKJA: transaction rejected by ApprovalProgram
```

Very cool, our last transaction simply rejected because you did not supply the desired parameter.

### Dealing with group transaction to implement atomic operations

Coming soon...


## Todos

 * Utilize Python type hints to able to use typed parameters on cli commands. Also code base would statically be more accurate and stable.
 * Different config sections should be selectable while tooling.
 * Unit tests.
 * More documentation and examples.


## Disclaimer

This project is in very early stages so please use it at your own risk.

## License

Copyright (c) 2021 Kadir Pekel.

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the 'Software'), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED 'AS IS', WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
