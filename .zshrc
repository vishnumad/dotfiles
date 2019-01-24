# Alias for dotfiles bare repository
alias config='/usr/bin/git --git-dir=$HOME/dotfiles/ --work-tree=$HOME'

#
# User configuration sourced by interactive shells
#

# Define zim location
export ZIM_HOME=${ZDOTDIR:-${HOME}}/.zim

# Start zim
[[ -s ${ZIM_HOME}/init.zsh ]] && source ${ZIM_HOME}/init.zsh

[ -f ~/.fzf.zsh ] && source ~/.fzf.zsh

# Add to path
export PATH=$HOME/.gem/ruby/2.5.0/bin:$PATH
