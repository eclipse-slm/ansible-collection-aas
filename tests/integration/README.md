1. Create the following directories in your home directory:
   ````shell
   mkdir -p ~/ansible_collections/slm
   ````
2. Clone the repository from your profile to the created path:
   ````shell
   git clone https://github.com/YOURACC/ansible-collection-aas.git ~/ansible_collections/slm/aas
   ````

3. Run tests
    ````shell
    ansible-test integration aas
    ````