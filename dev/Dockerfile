FROM ghcr.io/eclipse-slm/ansible:2.17.2

USER root

ENV CONSUL_URL=http://<your-consul-server>:8500 \
    CONSUL_TOKEN=<your-consul-token> \
    VAULT_URL=http://<your-vault-server>:8200 \
    VAULT_APPROLE_ROLE_ID=<your-vault-app-role-id> \
    VAULT_APPROLE_SECRET_ID=<your-vault-app-role-secret-id> \
    ANSIBLE_CMD_PARAMETERS="-v"

COPY .. /src

WORKDIR src

RUN ansible-galaxy install -r tests/requirements.yml

RUN pip install -r requirements.txt

CMD ansible-playbook ${ANSIBLE_CMD_PARAMETERS} run.yml
