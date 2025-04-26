# (after setting up container, installing Python, cloning repo, etc.)

echo "=== Setting up clean .bashrc ==="
pct exec $CT_ID -- bash -c "cat > /root/.bashrc << 'EOF'
# ~/.bashrc: executed by bash(1) for non-login shells.

# If not running interactively, don't do anything
[ -z \"\$PS1\" ] && return

# History settings
HISTCONTROL=ignoredups:ignorespace
HISTSIZE=1000
HISTFILESIZE=2000
shopt -s histappend

# Check window size after each command
shopt -s checkwinsize

# Lesspipe for friendly less
[ -x /usr/bin/lesspipe ] && eval \"\$(SHELL=/bin/sh lesspipe)\"

# Debian chroot environment
if [ -z \"\$debian_chroot\" ] && [ -r /etc/debian_chroot ]; then
    debian_chroot=\$(cat /etc/debian_chroot)
fi

# Force color prompt
force_color_prompt=yes

# Set color prompt
if [ -n \"\$force_color_prompt\" ]; then
    if [ -x /usr/bin/tput ] && tput setaf 1 >&/dev/null; then
        color_prompt=yes
    else
        color_prompt=
    fi
fi

if [ \"\$color_prompt\" = yes ]; then
    PS1='\${debian_chroot:+(\$debian_chroot)}\[\e[1;32m\]\u@\h:\w\[\e[0m\]\$ '
else
    PS1='\${debian_chroot:+(\$debian_chroot)}\u@\h:\w\$ '
fi
unset color_prompt force_color_prompt

# Terminal title
case \"\$TERM\" in
    xterm*|rxvt*)
        PS1=\"\[\e]0;\${debian_chroot:+(\$debian_chroot)}\u@\h: \w\a\]\$PS1\"
        ;;
esac

# Load color support for ls, grep, etc.
if [ -x /usr/bin/dircolors ]; then
    if [ -r ~/.dircolors ]; then
        eval \"\$(dircolors -b ~/.dircolors)\"
    else
        eval \"\$(dircolors -b)\"
    fi
fi

# Load bash aliases if available
if [ -f ~/.bash_aliases ]; then
    . ~/.bash_aliases
fi

# Grep color highlight
export GREP_COLOR='1;32'
EOF
"

echo "=== Creating .bash_aliases ==="
pct exec $CT_ID -- bash -c "cat > /root/.bash_aliases << 'EOF'
# ~/.bash_aliases

# Shell alias
alias sbash='source .bashrc'

# Directory navigation
alias ..='cd ..'
alias ...='cd ../..'

# Colored ls
alias ls='ls --color=auto'
alias ll='ls -alF --color=auto'
alias la='ls -A --color=auto'
alias l='ls -CF --color=auto'

# Grep color
alias grep='grep --color=auto'
alias fgrep='fgrep --color=auto'
alias egrep='egrep --color=auto'

# Handy commands
alias cls='clear'

# Filetools-specific shortcuts
alias update='/opt/jb-filetools/update.sh'
alias settings='nano /etc/filetools/settings.json'
alias appdir='cd /opt/jb-filetools'
alias transdir='cd /mnt/transmission'
alias filetools='/opt/jb-filetools/venv/bin/filetools'
EOF
"

echo "=== Setting global environment variables ==="
pct exec $CT_ID -- bash -c "echo 'FILETOOLS_SETTINGS=/etc/filetools/settings.json' >> /etc/environment"
pct exec $CT_ID -- bash -c "echo 'APP_VERSION=$APP_VERSION' >> /etc/environment"

echo "=== Disabling PAM systemd session hooks to speed up SSH ==="
pct exec $CT_ID -- sed -i 's/^session\s*required\s*pam_systemd\.so/#&/' /etc/pam.d/sshd
pct exec $CT_ID -- sed -i 's/^session\s*optional\s*pam_systemd\.so/#&/' /etc/pam.d/common-session

echo "=== Container $CT_ID created and configured ==="
echo "➡ Connect: ssh root@${CT_IP0%%/*}"
echo "➡ Aliases ready: appdir, filetools, settings, transdir, update"
echo "=== Done ==="
