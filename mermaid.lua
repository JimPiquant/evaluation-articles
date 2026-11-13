-- Render only into the publisher's isolated article/format directory.
-- A renderer error must abort Pandoc, never expose raw code or stale images.
local counter = 0

local function inches(value, maximum)
  if not value or value == "" or value == "auto" then
    return nil
  end
  local number, unit = value:match("^(%d*%.?%d+)([%a%%]*)$")
  number = tonumber(number)
  local units = {[""] = 1 / 72, ["in"] = 1, ["cm"] = 1 / 2.54,
    ["mm"] = 1 / 25.4, ["pt"] = 1 / 72, ["px"] = 1 / 96}
  if unit == "%" and number then
    return maximum * number / 100
  end
  if not number or not units[unit] or number <= 0 then
    error("Unsupported image dimension: " .. value)
  end
  return number * units[unit]
end

local function fit_image(image)
  local max_width = tonumber(os.getenv("PUBLISH_IMAGE_MAX_WIDTH"))
  local max_height = tonumber(os.getenv("PUBLISH_IMAGE_MAX_HEIGHT"))
  if not max_width or not max_height then
    error("Image bounds are required; use scripts/publish.py")
  end
  local file = assert(io.open(image.src, "rb"))
  local bytes = file:read("*a")
  file:close()
  local size = pandoc.image.size(bytes)
  local width = size.width / (size.dpi_horz or 72)
  local height = size.height / (size.dpi_vert or 72)
  if width <= 0 or height <= 0 then
    error("Image has invalid dimensions: " .. image.src)
  end
  local desired_width = inches(image.attributes.width, max_width)
  local desired_height = inches(image.attributes.height, max_height)
  local scale = 1
  if desired_width and desired_height then
    scale = math.min(desired_width / width, desired_height / height)
  elseif desired_width then
    scale = desired_width / width
  elseif desired_height then
    scale = desired_height / height
  end
  scale = math.min(scale, max_width / width, max_height / height)
  image.attributes.width = string.format("%.6fin", width * scale)
  image.attributes.height = string.format("%.6fin", height * scale)
  local layout = os.getenv("PUBLISH_IMAGE_LAYOUT")
  if layout then
    local records = assert(io.open(layout, "a"))
    records:write(pandoc.json.encode({
      source = image.src, width = width * scale, height = height * scale,
      alt = pandoc.utils.stringify(image.caption)
    }) .. "\n")
    records:close()
  end
  return image
end

function Image(image)
  return fit_image(image)
end

function CodeBlock(block)
  if not block.classes:includes("mermaid") then
    return nil
  end
  local directory = os.getenv("PUBLISH_ASSET_DIR")
  if not directory or directory == "" then
    error("Mermaid requires PUBLISH_ASSET_DIR; use scripts/publish.py")
  end
  pandoc.system.make_directory(directory, true)
  counter = counter + 1
  local name = string.format("diagram-%02d-%s", counter,
    pandoc.utils.sha1(block.text):sub(1, 16))
  local infile = directory .. "/" .. name .. ".mmd"
  local outfile = directory .. "/" .. name .. ".png"
  local source = assert(io.open(infile, "w"))
  assert(source:write(block.text))
  assert(source:close())
  os.remove(outfile)

  local args = {"--input", infile, "--output", outfile,
    "--backgroundColor", "white", "--scale", "2", "--quiet"}
  local config = os.getenv("PUBLISH_MERMAID_CONFIG")
  if config and config ~= "" then
    table.insert(args, "--configFile")
    table.insert(args, config)
  end
  local browser = os.getenv("PUBLISH_PUPPETEER_CONFIG")
  if browser and browser ~= "" then
    table.insert(args, "--puppeteerConfigFile")
    table.insert(args, browser)
  end
  local ok, result = pcall(pandoc.pipe, os.getenv("PUBLISH_MMDC") or "mmdc", args, "")
  if not ok then
    os.remove(outfile)
    error("Mermaid render failed for " .. name .. ": " .. tostring(result))
  end
  local image = io.open(outfile, "rb")
  if not image then
    error("Mermaid renderer returned success without an image: " .. name)
  end
  local magic = image:read(8)
  local size = image:seek("end")
  image:close()
  if magic ~= "\137PNG\r\n\26\n" or size <= 8 then
    os.remove(outfile)
    error("Mermaid renderer produced an invalid PNG: " .. name)
  end
  local alt = block.attributes.alt or block.attributes.caption
    or ("Evaluation diagram " .. counter .. " (see accompanying explanation)")
  return pandoc.Para({fit_image(pandoc.Image({pandoc.Str(alt)}, outfile, ""))})
end
