function! StaticColors() abort
    " Status line color
    hi StatusLine     cterm=NONE ctermbg=NONE    ctermfg=7
    hi StatusLineNC   cterm=NONE ctermbg=NONE ctermfg=8
    hi User1          cterm=NONE ctermbg=8    ctermfg=NONE
    hi User3          cterm=NONE ctermbg=0    ctermfg=NONE
    
    hi VertSplit      cterm=NONE ctermbg=NONE ctermfg=8
    hi CursorLine     cterm=NONE ctermbg=0    ctermfg=NONE
    hi MatchParen     cterm=NONE ctermbg=8    ctermfg=1
    hi Folded                    ctermbg=0    ctermfg=3
    hi Visual                    ctermbg=4    ctermfg=0
    hi LineNr         cterm=NONE ctermbg=NONE ctermfg=8
    hi EndOfBuffer    cterm=NONE ctermbg=NONE ctermfg=8
    hi CursorLineNr   cterm=NONE ctermbg=0    ctermfg=4
endfunction

syntax on
set background=dark
set t_Co=256

call StaticColors()
