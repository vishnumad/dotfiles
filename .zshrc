# Auto-Install ZPlugin {{{

ZPLUGIN="${ZDOTDIR:-$HOME}/.zplugin/bin/zplugin.zsh"

if [[ ! -f "$ZPLUGIN" ]]; then
  if (( $+commands[git] )); then
    sh -c "$(curl -fsSL https://raw.githubusercontent.com/zdharma/zplugin/master/doc/install.sh)"
  else
    echo 'git not found' >&2
    exit 1
  fi
fi

source "$ZPLUGIN"
autoload -Uz _zplugin
(( ${+_comps} )) && _comps[zplugin]=_zplugin

# }}}

# ZPlugin {{{

# Prompt
zplugin light subnixr/minimal

zplugin ice wait"1" lucid atload"_zsh_autosuggest_start"
zplugin light zsh-users/zsh-autosuggestions

zplugin ice wait"0" blockf lucid
zplugin light zsh-users/zsh-completions

# Syntax highlighting
zplugin ice lucid atinit"zpcompinit; zpcdreplay"
zplugin light zdharma/fast-syntax-highlighting

# NVM
zplugin ice wait"1" lucid
zplugin light lukechilds/zsh-nvm

# }}}

for file in ~/.zshrc.d/*.zshrc;
do
    source "${file}"
done

# Prompt Customization
MNML_RPROMPT=(mnml_git 'mnml_cwd 5 8')
MNML_INFOLN=(mnml_err mnml_jobs mnml_uhp)

# Lazy load NVM
export NVM_LAZY_LOAD=true

# Highlight zsh selections
zstyle ':completion:*' menu select

# Case insensitive completions
zstyle ':completion:*' matcher-list 'm:{a-zA-Z}={A-Za-z}' 'r:|[._-]=* r:|=*' 'l:|=* r:|=*'

setopt autocd

# Vi Mode
bindkey -v
export KEYTIMEOUT=1

# Load keybindings for Delete key and others
autoload zkbd
zkbd_file_loc="$TERM-:0"
[[ ! -f ${ZDOTDIR:-$HOME}/.zkbd/$zkbd_file_loc ]] && zkbd
source ${ZDOTDIR:-$HOME}/.zkbd/$zkbd_file_loc

[[ -n ${key[Backspace]} ]] && bindkey "${key[Backspace]}" backward-delete-char
[[ -n ${key[Insert]} ]] && bindkey "${key[Insert]}" overwrite-mode
[[ -n ${key[Home]} ]] && bindkey "${key[Home]}" beginning-of-line
[[ -n ${key[PageUp]} ]] && bindkey "${key[PageUp]}" up-line-or-history
[[ -n ${key[Delete]} ]] && bindkey "${key[Delete]}" delete-char
[[ -n ${key[End]} ]] && bindkey "${key[End]}" end-of-line
[[ -n ${key[PageDown]} ]] && bindkey "${key[PageDown]}" down-line-or-history
[[ -n ${key[Up]} ]] && bindkey "${key[Up]}" up-line-or-search
[[ -n ${key[Left]} ]] && bindkey "${key[Left]}" backward-char
[[ -n ${key[Down]} ]] && bindkey "${key[Down]}" down-line-or-search
[[ -n ${key[Right]} ]] && bindkey "${key[Right]}" forward-char

# Shift+Tab
bindkey '^[[Z' reverse-menu-complete

# Add to path
export PATH=$HOME/.gem/ruby/2.5.0/bin:$PATH
export PATH=$HOME/.gem/ruby/2.6.0/bin:$PATH
export PATH=$HOME/.local/bin:$PATH
