--[[
  mermaid.lua — Pandoc Lua filter that renders Mermaid code blocks to PNG.

  Requires mmdc (npm install -g @mermaid-js/mermaid-cli) on PATH.

  For each ```mermaid code block, writes the source to a temp file,
  invokes mmdc to produce a PNG, and replaces the block with an image.
  Images are written to an `img/` subdirectory next to the output file.
]]

local counter = 0
local img_dir = "img"

local function ensure_dir(dir)
  os.execute("mkdir -p " .. dir)
end

function CodeBlock(block)
  if block.classes[1] ~= "mermaid" then
    return nil
  end

  counter = counter + 1
  ensure_dir(img_dir)

  local infile = os.tmpname() .. ".mmd"
  local outfile = img_dir .. "/mermaid-" .. counter .. ".png"

  local f = io.open(infile, "w")
  f:write(block.text)
  f:close()

  local cmd = string.format(
    'mmdc -i "%s" -o "%s" -b transparent --scale 2 2>&1',
    infile, outfile
  )
  local handle = io.popen(cmd)
  local result = handle:read("*a")
  handle:close()

  os.remove(infile)

  if io.open(outfile, "r") then
    return pandoc.Para({pandoc.Image({}, outfile, "")})
  else
    io.stderr:write("Warning: mmdc failed for diagram " .. counter .. "\n")
    io.stderr:write(result .. "\n")
    return block
  end
end
