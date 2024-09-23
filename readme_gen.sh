# basic
rm -rf readme.md
cp readme.in readme.md

# five most recently modified
echo "# Top Five Newest" >> readme.md
echo "\`\`\`" >> readme.md
find . -type f -name "*.md" ! -iname "readme.md" -exec stat -f "%m %N" {} + | sort -n | tail -5 | sort -nr | cut -d' ' -f2- >> readme.md
echo "\`\`\`\n" >> readme.md

# directory tree
echo "# Directory Tree" >> readme.md
echo "\`\`\`" >> readme.md
tree -P "*.md" -I "*.assets" >> readme.md
echo "\`\`\`\n" >> readme.md
