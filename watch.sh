watch -n 10 -d echo "Proc [\`grep \"blog_image=>\" out.log | wc -l\`] \| Not Seen [\`grep \"not seen\" out.log | wc -l\`] Seen [\`grep \"have seen\" out.log | wc -l\`] \| Saved [\`grep \"save:\" out.log | wc -l\`]"