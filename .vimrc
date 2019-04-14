" Plugins {{{

" Auto install vim-plug
if empty(glob('~/.vim/autoload/plug.vim'))
  silent !curl -fLo ~/.vim/autoload/plug.vim --create-dirs
    \ https://raw.githubusercontent.com/junegunn/vim-plug/master/plug.vim
  autocmd VimEnter * PlugInstall --sync | source $MYVIMRC
endif

" Load plugins
call plug#begin('~/.vim/plugged')
Plug 'vim-airline/vim-airline'        " vim-airline
Plug 'vim-airline/vim-airline-themes'
call plug#end()

" }}}

" Misc {{{

set nocompatible

inoremap jk <esc>

set background=dark
set t_Co=256

set breakindent
set linebreak

" Show line numbers
set number

" Hide vim's insert/visual/normal hints
set noshowmode

" Prevent delay for lightline when switching modes
set ttimeoutlen=50

" Save files as sudo with :W
cmap W w !sudo tee % > /dev/null

" Airline tabs
let g:airline#extensions#tabline#enabled = 1

" Airline theme
let g:airline_theme='deus'

" Airline font symbols
let g:airline_powerline_fonts = 1

if !exists('g:airline_symbols')
    let g:airline_symbols = {}
endif

" powerline symbols
let g:airline_left_sep = ''
let g:airline_left_alt_sep = ''
let g:airline_right_sep = ''
let g:airline_right_alt_sep = ''
let g:airline_symbols.branch = 'br'
let g:airline_symbols.readonly = 'ro'
let g:airline_symbols.linenr = ''
let g:airline_symbols.maxlinenr = ''

syntax on

set laststatus=2

set scrolljump=5
set scrolloff=3

set splitright
set splitbelow

set pumheight=20

" Wildmenu
set wildmenu
set winminheight=0
set wildmode=longest:full,full

" Search
set incsearch
set hlsearch

" Change cursor in Insert mode
let &t_SI = "\<Esc>[6 q"
let &t_SR = "\<Esc>[4 q"
let &t_EI = "\<Esc>[2 q"

" Highlight cursorline
set cursorline
hi CursorLine cterm=NONE ctermbg=0 ctermfg=NONE

" Parentheses highlight color
hi MatchParen cterm=NONE ctermbg=8 ctermfg=magenta

" Folded section color
hi Folded ctermbg=8

" }}}

" Spaces/Tabs {{{

set shiftwidth=4
set softtabstop=4
set tabstop=4
set smarttab
set expandtab

" }}}

" System Clipboard {{{

inoremap <C-v> <ESC>"+pa
vnoremap <C-c> "+y
vnoremap <C-d> "+d

" }}}

" Auto Groups {{{

augroup configgroup
    autocmd!
    autocmd VimEnter * highlight clear SignColumn
    autocmd BufWritePre *.php,*.py,*.js,*.txt,*.hs,*.java,*.md
                \:call <SID>StripTrailingWhitespaces()
    autocmd FileType java setlocal noexpandtab
    autocmd FileType java setlocal list
    autocmd FileType java setlocal listchars=tab:+\ ,eol:-
    autocmd FileType java setlocal formatprg=par\ -w80\ -T4
    autocmd FileType php setlocal expandtab
    autocmd FileType php setlocal list
    autocmd FileType php setlocal listchars=tab:+\ ,eol:-
    autocmd FileType php setlocal formatprg=par\ -w80\ -T4
    autocmd FileType ruby setlocal tabstop=2
    autocmd FileType ruby setlocal shiftwidth=2
    autocmd FileType ruby setlocal softtabstop=2
    autocmd FileType ruby setlocal commentstring=#\ %s
    autocmd FileType python setlocal commentstring=#\ %s
    autocmd BufEnter *.cls setlocal filetype=java
    autocmd BufEnter *.zsh-theme setlocal filetype=zsh
    autocmd BufEnter Makefile setlocal noexpandtab
    autocmd BufEnter *.sh setlocal tabstop=2
    autocmd BufEnter *.sh setlocal shiftwidth=2
    autocmd BufEnter *.sh setlocal softtabstop=2
augroup END

" }}}

" Code Folding {{{

set foldenable
set foldmethod=marker
set foldlevel=0
set modelines=1
nnoremap <space> za

" }}}

" vim:foldmethod=marker:foldlevel=0
