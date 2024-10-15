## How to run

The following command is used to test the modules located at "plugins/modules/"

````shell
ansible-playbook -M /tmp/roles/plugins/modules run_module.yml
````

...or:

````shell
export ANSIBLE_LIBRARY=/tmp/roles/plugins/modules
ansible-playbook run_module.yml
````
