a=(f e d c b a)
b=(`echo "${a[*]}" | tr ' ' "\n" | sort`)
echo ${b[*]}