source ~/.vim/startup/plugins.vim
source ~/.vim/startup/colors.vim
source ~/.vim/startup/statusline.vim
source ~/.vim/startup/autocommands.vim

inoremap jk <esc>

nnoremap <leader>ev <C-w><C-v><C-l>:e $MYVIMRC<cr>
nnoremap <leader>sv :source $MYVIMRC<cr>

set breakindent
set linebreak

" Show line numbers
set number

" Show column info in Ctrl+G
set noruler

" Prevent delay for lightline when switching modes
set ttimeoutlen=50

filetype plugin on

" Upper case word 
inoremap <leader>u <esc>viwUea
nnoremap <leader>u viwU<esc>e

" Show color column
set colorcolumn=+1
let &colorcolumn = join(range(81,999), ',')

" Save files as sudo with :W
cmap W w !sudo tee % > /dev/null

set scrolljump=5
set scrolloff=3

" vim command prompt
nnoremap <Space> :
vnoremap <Space> :

" Quickly show buffer list
nnoremap <F5> :buffers<CR>:

" Disable netrw banner
let g:netrw_banner=0

" Open splits by default to the right and below
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

" Split characters
set fillchars+=vert:│

" Highlight cursorline
set cursorline

" Tabs
set shiftwidth=4
set softtabstop=4
set tabstop=8
set smarttab
set expandtab

" System Clipboard 
inoremap <C-v> <ESC>"+pa
vnoremap <C-c> "+y
vnoremap <C-d> "+d

" Code Folding
set foldenable
set foldmethod=marker
set foldlevel=0
set modelines=1
nnoremap <Tab> za
