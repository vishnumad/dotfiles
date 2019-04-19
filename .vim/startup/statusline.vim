scriptencoding utf-8

function! StatuslineGitBranch() abort
  let b:gitbranch=""
  if &modifiable
    lcd %:p:h
    let l:gitrevparse=system("git rev-parse --abbrev-ref HEAD")
    lcd -
    if l:gitrevparse!~"fatal: not a git repository"
      let b:gitbranch=substitute(l:gitrevparse, '\n', '', 'g')
    endif
  endif
endfunction

function! GetBranchName() abort
    if exists("b:gitbranch") && strlen(b:gitbranch) > 0
        return (" ").b:gitbranch.(" ")
    endif
    return ""
endfunction


augroup GetGitBranch
  autocmd!
  autocmd VimEnter,WinEnter,BufEnter * call StatuslineGitBranch()
augroup END


" Status Line
set laststatus=2
set statusline=
set statusline+=%1*\ %<%t%h%w%m%r\ %*                " File path + mods
set statusline+=%3*%{GetBranchName()}%*              " Git branch
set statusline+=%=                                   " Spacer
set statusline+=%3*\ %l\ of\ %L\ %*                  " Line info
set statusline+=%1*\ B%n\ %*                         " Buffer number

