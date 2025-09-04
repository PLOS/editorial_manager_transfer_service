# Editorial Manager Transfer Service
A plugin to provide information for Aries' Editorial Manager to enable automatic transfers.

## Requirements
This plugin depends on the Production Transporter plugin in order to work properly.

## Development Tips
This section contains guidance for developing this plugin. 

For the purposes of this guide we'll refer to the Janeway installation folder as `[workspace]`. 

The plugin's installation folder is assumed to be `[workspace]/src/plugins/editorial_manager_transfer_service`.

### Adding The Janeway SRC to the `PYTHONPATH`
Adding the Janeway SRC folder to the `PYTHONPATH` can help any type of IDE correctly identify imports while developing plugins.

#### Instructions for Python Virtual Environment (VENV)
First, open your `activate` file in a text editor. It is located at:
```text
[workspace]/.venv/bin/activate
```
Once open, scroll to find the following text section:
```bash
VIRTUAL_ENV="[workspace]/.venv"
if ([ "$OSTYPE" = "cygwin" ] || [ "$OSTYPE" = "msys" ]) && $(command -v cygpath &> /dev/null) ; then
    VIRTUAL_ENV=$(cygpath -u "$VIRTUAL_ENV")
fi
export VIRTUAL_ENV


_OLD_VIRTUAL_PATH="$PATH"
PATH="$VIRTUAL_ENV/bin:$PATH"
export PATH
```
Please note and change the `[worksapce]` variable to your Janeway installation path. 

You will modify this section to become the following:
```bash
_PYTHON_ENV_PKG='[workspace]'
VIRTUAL_ENV="$_PYTHON_ENV_PKG/.venv"
if ([ "$OSTYPE" = "cygwin" ] || [ "$OSTYPE" = "msys" ]) && $(command -v cygpath &> /dev/null) ; then
    VIRTUAL_ENV=$(cygpath -u "$VIRTUAL_ENV")
fi
export VIRTUAL_ENV

_OLD_VIRTUAL_PATH="$PATH"
PATH="$VIRTUAL_ENV/bin:$PATH"
export PATH

_OLD_VIRTUAL_PYTHONPATH="$PYTHONPATH"
PYTHONPATH="$_PYTHON_ENV_PKG:$PYTHONPATH"
export PYTHONPATH
```
Next you will modify the `deactivate()` script. Scroll until you find this section of script:
```bash
deactivate () {
    unset -f pydoc >/dev/null 2>&1 || true

    # reset old environment variables
    # ! [ -z ${VAR+_} ] returns true if VAR is declared at all
    if ! [ -z "${_OLD_VIRTUAL_PATH:+_}" ] ; then
        PATH="$_OLD_VIRTUAL_PATH"
        export PATH
        unset _OLD_VIRTUAL_PATH
    fi
    if ! [ -z "${_OLD_VIRTUAL_PYTHONHOME+_}" ] ; then
        PYTHONHOME="$_OLD_VIRTUAL_PYTHONHOME"
        export PYTHONHOME
        unset _OLD_VIRTUAL_PYTHONHOME
    fi
```
Modify it to add the `PYTHONPATH` deactivation:
```bash
        ...
        unset _OLD_VIRTUAL_PATH
    fi
    if ! [ -z "${_OLD_VIRTUAL_PYTHONPATH:+_}" ] ; then
        PYTHONPATH="$_OLD_VIRTUAL_PYTHONPATH"
        export PYTHONPATH
        unset _OLD_VIRTUAL_PYTHONPATH
    fi
    if ! [ -z "${_OLD_VIRTUAL_PYTHONHOME+_}" ] ; then
      ...
```
After restarting your IDE, you should see it properly detect the SRC folder.