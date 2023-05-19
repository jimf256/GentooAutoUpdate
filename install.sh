#!/bin/bash

# install the openrc init script
rm /etc/init.d/update_portage 2>/dev/null
cp init_script/update_portage /etc/init.d/

# install the post-kernel-install hook
rm /etc/kernel/postinst.d/90-update-grub-custom-option 2>/dev/null
cp kernel_install_hook/90-update-grub-custom-option /etc/kernel/postinst.d/
