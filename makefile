default:
	sudo iptables -A INPUT -p tcp --dport 7734 -j ACCEPT
	sudo iptables -A OUTPUT -p tcp --dport 7734 -j ACCEPT
	sudo iptables -A INPUT -p tcp --dport 3000 -j ACCEPT
	sudo iptables -A OUTPUT -p tcp --dport 3000 -j ACCEPT
	sudo iptables -A INPUT -p tcp --dport 4000 -j ACCEPT
	sudo iptables -A OUTPUT -p tcp --dport 4000 -j ACCEPT
	sudo iptables -A INPUT -p tcp --dport 5000 -j ACCEPT
	sudo iptables -A OUTPUT -p tcp --dport 5000 -j ACCEPT
	sudo iptables -A INPUT -p tcp --dport 6000 -j ACCEPT
	sudo iptables -A OUTPUT -p tcp --dport 6000 -j ACCEPT
	sudo iptables -A INPUT -p tcp --dport 7000 -j ACCEPT
	sudo iptables -A OUTPUT -p tcp --dport 7000 -j ACCEPT
	sudo iptables -A INPUT -p tcp --dport 8000 -j ACCEPT
	sudo iptables -A OUTPUT -p tcp --dport 8000 -j ACCEPT