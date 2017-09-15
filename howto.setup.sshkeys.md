howto.setup.sshkeys

https://www.digitalocean.com/community/tutorials/how-to-configure-ssh-key-based-authentication-on-a-linux-server

generate public/private keypair using ssh-keygen

ssh-keygen

# private key /.ssh/id_rsa
# public key  /.ssh/id_rsa.pub

- go through wizard, accept defaults
- take generated public key and place it on remove server

# get pub key on client, add it to list of authorized keys on server

cat ~/.ssh/id_rsa.pub

	# content will look like "ssh-rsa AAAAB3NzaC1yc2EA..."

# SSH into server, add pub key to ~/.ssh/authorized_keys
- or - 
# use ssh-copy-id user@host (-p <port>)

ssh-copy-id jeremy@s.blacksky.us -p 51500
## warning: whit appears to cause fail2ban to lock me out


optional: disable password based auth
sudo nano /etc/ssh/sshd_config
PasswordAuthentication no
sudo service ssh restart
