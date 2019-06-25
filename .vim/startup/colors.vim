function! LightColors() abort
    " Status line color
    hi StatusLine     cterm=NONE    ctermbg=NONE    ctermfg=7
    hi StatusLineNC   cterm=NONE    ctermbg=NONE    ctermfg=8
    hi User1          cterm=NONE    ctermbg=0       ctermfg=15
    hi User3          cterm=NONE    ctermbg=7       ctermfg=NONE
    
    hi VertSplit      cterm=NONE    ctermbg=NONE    ctermfg=8
    hi CursorLine     cterm=NONE    ctermbg=7       ctermfg=NONE
    hi MatchParen     cterm=NONE    ctermbg=8       ctermfg=1
    hi Folded                       ctermbg=8       ctermfg=15
    hi Visual                       ctermbg=7       ctermfg=8
    hi LineNr         cterm=NONE    ctermbg=NONE    ctermfg=8
    hi EndOfBuffer    cterm=NONE    ctermbg=NONE    ctermfg=8
    hi CursorLineNr   cterm=NONE    ctermbg=7       ctermfg=8
    hi ColorColumn    cterm=NONE    ctermbg=NONE    ctermfg=1
endfunction

function! DarkColors() abort
    hi StatusLine     cterm=NONE    ctermbg=NONE    ctermfg=8
    hi StatusLineNC   cterm=NONE    ctermbg=NONE    ctermfg=8
    hi User1          cterm=NONE    ctermbg=7       ctermfg=0
    hi User3          cterm=NONE    ctermbg=0       ctermfg=7
    
    hi VertSplit      cterm=NONE    ctermbg=NONE    ctermfg=8
    hi CursorLine     cterm=NONE    ctermbg=0       ctermfg=NONE
    hi MatchParen     cterm=NONE    ctermbg=7       ctermfg=1
    hi Folded                       ctermbg=0       ctermfg=11
    hi Visual                       ctermbg=8       ctermfg=15
    hi LineNr         cterm=NONE    ctermbg=NONE    ctermfg=8
    hi EndOfBuffer    cterm=NONE    ctermbg=NONE    ctermfg=7
    hi CursorLineNr   cterm=NONE    ctermbg=0       ctermfg=7
    hi ColorColumn    cterm=NONE    ctermbg=NONE    ctermfg=9
endfunction

syntax on
set t_Co=256

if &term=~'linux'
    " Linux console (tty)
    set background=dark
    call DarkColors()
else
    " Normal
    set background=dark
    call DarkColors()
endif
