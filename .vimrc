" Plugins {{{

" Auto install vim-plug
if empty(glob('~/.vim/autoload/plug.vim'))
  silent !curl -fLo ~/.vim/autoload/plug.vim --create-dirs
    \ https://raw.githubusercontent.com/junegunn/vim-plug/master/plug.vim
  autocmd VimEnter * PlugInstall --sync | source $MYVIMRC
endif

" Load plugins
call plug#begin('~/.vim/plugged')
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

" Prevent delay for lightline when switching modes
set ttimeoutlen=50

" Save files as sudo with :W
cmap W w !sudo tee % > /dev/null

syntax on

set scrolljump=5
set scrolloff=3

" vim command prompt
nnoremap <Space> :
vnoremap <Space> :

" Quickly Show/Switch Buffers
nnoremap <F5> :buffers<CR>:buffer<Space>

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

" Change cursor in different modes
let &t_SI = "\<Esc>[6 q"
let &t_SR = "\<Esc>[4 q"
let &t_EI = "\<Esc>[2 q"

function! CurrentGitBranch()
  return system("git rev-parse --abbrev-ref HEAD 2>/dev/null | tr -d '\n'")
endfunction

function! StatusGitInfo()
  let l:branchname = CurrentGitBranch()
  return strlen(l:branchname) > 0?'  '.l:branchname.' ':''
endfunction

" Status Line
set laststatus=2
set statusline=
set statusline+=%1*\ %n\ %*            " Buffer number
set statusline+=\ %f%h%w\ %m           " File path
set statusline+=%2*\ %R\ %*            " Read-only
set statusline+=%=                     " Spacer
set statusline+=\ %{StatusGitInfo()}   " Git branch
set statusline+=%1*\ %-3c\ \ %4l/%-4L\ \ %3P\ %*   " Line/Column Info

" Status line color
hi StatusLine cterm=NONE ctermbg=0 ctermfg=white
hi StatusLineNC cterm=NONE ctermbg=NONE ctermfg=8
hi User1 cterm=NONE ctermbg=8 ctermfg=NONE
hi User2 cterm=NONE ctermbg=0 ctermfg=red

" Split characters
set fillchars+=vert:│
hi VertSplit cterm=NONE ctermbg=NONE ctermfg=8

" Highlight cursorline
set cursorline
hi CursorLine cterm=NONE ctermbg=0 ctermfg=NONE

" Parentheses highlight color
hi MatchParen cterm=NONE ctermbg=8 ctermfg=magenta

" Folded section color
hi Folded ctermbg=8

" Selection color
hi Visual ctermbg=4 ctermfg=0

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

"autocmd FileType netrw nnoremap q :bd<CR>

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
nnoremap <Tab> za

" }}}

" vim:foldmethod=marker:foldlevel=0
