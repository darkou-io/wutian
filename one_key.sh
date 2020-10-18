comment=$1
if [ -z "$comment" ]; then
    comment='developing'
fi

# make build
# if [ $? -ne 0 ]; then
#     echo 'build failed'
#     exit 1
# fi

git commit -am"$comment" && git push
