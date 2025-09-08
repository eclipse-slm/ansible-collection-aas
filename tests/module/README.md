## How to run

The following command is used to test the modules located at "plugins/modules/"

````shell
ansible-playbook -v -M /src/plugins/modules run_module.yml
````

...or:

````shell
export ANSIBLE_LIBRARY=/src/plugins/modules
ansible-playbook -v run_module.yml
````
