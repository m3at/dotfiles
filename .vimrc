set runtimepath+=~/.vim_runtime

execute pathogen#infect()

source ~/.vim_runtime/vimrcs/basic.vim
source ~/.vim_runtime/vimrcs/filetypes.vim
source ~/.vim_runtime/vimrcs/plugins_config.vim
source ~/.vim_runtime/vimrcs/extended.vim

try
    source ~/.vim_runtime/my_configs.vim
catch
endtry


let g:jedi#popup_on_dot = 0
set noerrorbells visualbell t_vb= " mute bell sound
set autoindent          " always set autoindenting on
set smartindent         " smart indent
set tags+=tags;
set showtabline=0
" let g:airline#extensions#tabline#buffer_min_count =2
" ~/.vim_runtime/sources_non_forked/vim-airline/autoload/airline/extensions/tabline/autoshow.vim line 5 -> 2
