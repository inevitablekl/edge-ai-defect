-- Phase 4.5 Full-manuscript bridge.
-- Converts the accepted Markdown front matter/comments into named styles,
-- inserts the accepted final figure assets, and keeps identity metadata local.

local function meta_text(meta, key)
  local value = meta[key]
  if value == nil then
    return ""
  end
  return pandoc.utils.stringify(value)
end

local function meta_flag(meta, key)
  local value = meta[key]
  if value == nil then
    return false
  end
  return string.lower(pandoc.utils.stringify(value)) == "true"
end

local function metadata_value(value)
  if value == nil then
    return ""
  end
  return pandoc.utils.stringify(value)
end

local function author_biography_text(meta)
  -- Phase 7.1 accepts structured author-biographies. Empty records are data
  -- gaps, not text to invent. Keep author-biography as a backward-compatible
  -- local metadata fallback for existing review builds.
  local records = meta["author-biographies"]
  if records ~= nil and records.t == "MetaList" then
    local output = {}
    for _, record in ipairs(records) do
      if record.t == "MetaMap" then
        local biography = metadata_value(record["biography-cn"])
        if biography ~= "" then
          biography = biography:gsub("。$", "")
          local corresponding = string.lower(metadata_value(record["corresponding"])) == "true"
          local email = metadata_value(record["email"])
          if corresponding and not biography:find("通信作者", 1, true) then
            biography = biography .. "，通信作者"
          end
          if corresponding and email ~= "" and not biography:find("E-mail:", 1, true) then
            biography = biography .. "，E-mail:" .. email
          end
          table.insert(output, biography)
        end
      end
    end
    if #output > 0 then
      return table.concat(output, "；") .. "。"
    end
  end
  return meta_text(meta, "author-biography")
end

local function style_attr(style)
  return pandoc.Attr("", {}, {{"custom-style", style}})
end

local function styled_inlines(inlines, style)
  return pandoc.Div({pandoc.Para(inlines)}, style_attr(style))
end

local function styled_text(text, style)
  return styled_inlines({pandoc.Str(text)}, style)
end

local function mixed_front_matter(block, body_style, label, label_style, add_space)
  local inlines = pandoc.Inlines{
    pandoc.Span({pandoc.Str(label)}, style_attr(label_style))
  }
  if add_space then
    inlines:insert(pandoc.Space())
  end
  inlines:extend(block.content)
  return styled_inlines(inlines, body_style)
end

local function block_text(block)
  if block.t == "Para" or block.t == "Plain" or block.t == "Header" then
    return pandoc.utils.stringify(block.content)
  end
  return ""
end

local function styled_block(block, style)
  if block.t == "Para" or block.t == "Plain" then
    return pandoc.Div({pandoc.Para(block.content)}, style_attr(style))
  end
  return pandoc.Div({pandoc.Para(block.content)}, style_attr(style))
end

local function add_full_identity(output, meta, language, anonymous)
  if anonymous then
    return
  end
  if language == "cn" then
    output:insert(styled_text(meta_text(meta, "authors-cn"), "HFUTAuthorsCN"))
    output:insert(styled_text(meta_text(meta, "affiliation-cn"), "HFUTAffiliationCN"))
  else
    output:insert(styled_text(meta_text(meta, "authors-en"), "HFUTAuthorsEN"))
    output:insert(styled_text(meta_text(meta, "affiliation-en"), "HFUTAffiliationEN"))
  end
end

local function add_final_front_matter(output, meta, anonymous)
  output:insert(styled_text(
    "中图分类号：" .. meta_text(meta, "classification") .. "　文献标识码：" .. meta_text(meta, "document-code"),
    "HFUTClassification"
  ))
  local biography = author_biography_text(meta)
  if not anonymous and biography ~= "" then
    output:insert(styled_text(biography, "HFUTAuthorBiography"))
  end
end

local function figure_block(path, width)
  local image = pandoc.Image(
    {},
    path,
    "",
    pandoc.Attr("", {}, {{"width", width}})
  )
  return pandoc.Para({image})
end

local function figure_for_caption(text)
  if text:match("^图1　") then
    return "fig1_input_data_path_model_phase59c.png"
  elseif text:match("^图2　") then
    return "fig3_main_e2e_phase56.png"
  elseif text:match("^图3　") then
    return "fig4_run_level_distribution_phase56.png"
  end
  return nil
end

local function figure_width(text)
  if text:match("^图1　") then
    return "16cm"
  end
  return "7.5cm"
end

function Pandoc(doc)
  local output = pandoc.Blocks{}
  local anonymous = meta_flag(doc.meta, "anonymous-review")
  local front_matter = true
  local pending = nil
  local final_front_matter_added = false

  for _, block in ipairs(doc.blocks) do
    local text = block_text(block)

    if front_matter and block.t == "Header" and block.level == 1 and text == "题名与摘要" then
      -- The source packet label is governance metadata, not publication prose.
    elseif front_matter and block.t == "Header" and block.level == 2 then
      local labels = {
        ["中文题名"] = "cn_title",
        ["中文摘要"] = "cn_abstract",
        ["中文关键词"] = "cn_keywords",
        ["English Title"] = "en_title",
        ["English Abstract"] = "en_abstract",
        ["English Keywords"] = "en_keywords",
      }
      pending = labels[text]
    elseif front_matter and block.t == "Header" and block.level == 1 and text == "0 引 言" then
      front_matter = false
      output:insert(styled_text("FULL_BODY_SECTION_START", "HFUTSpecimenNotice"))
      output:insert(styled_inlines(block.content, "HFUTHeading1"))
    elseif front_matter and pending == "cn_title" and (block.t == "Para" or block.t == "Plain") then
      output:insert(styled_block(block, "HFUTTitleCN"))
      add_full_identity(output, doc.meta, "cn", anonymous)
      pending = nil
    elseif front_matter and pending == "cn_abstract" and (block.t == "Para" or block.t == "Plain") then
      output:insert(mixed_front_matter(block, "HFUTAbstractBodyCN", "摘 要：", "HFUTAbstractLabelCNChar", false))
      pending = nil
    elseif front_matter and pending == "cn_keywords" and (block.t == "Para" or block.t == "Plain") then
      output:insert(mixed_front_matter(block, "HFUTKeywordsBodyCN", "关键词：", "HFUTKeywordsLabelCNChar", false))
      pending = nil
    elseif front_matter and pending == "en_title" and (block.t == "Para" or block.t == "Plain") then
      output:insert(styled_block(block, "HFUTTitleEN"))
      add_full_identity(output, doc.meta, "en", anonymous)
      pending = nil
    elseif front_matter and pending == "en_abstract" and (block.t == "Para" or block.t == "Plain") then
      output:insert(mixed_front_matter(block, "HFUTAbstractBodyEN", "Abstract:", "HFUTAbstractLabelENChar", true))
      pending = nil
    elseif front_matter and pending == "en_keywords" and (block.t == "Para" or block.t == "Plain") then
      output:insert(mixed_front_matter(block, "HFUTKeywordsBodyEN", "Key words：", "HFUTKeywordsLabelENChar", true))
      pending = nil
      if not final_front_matter_added then
        add_final_front_matter(output, doc.meta, anonymous)
        final_front_matter_added = true
      end
    elseif not front_matter and block.t == "Header" then
      local style = "HFUTHeading3"
      if block.level == 1 then
        style = "HFUTHeading1"
      elseif block.level == 2 then
        style = "HFUTHeading2"
      end
      output:insert(styled_inlines(block.content, style))
    elseif not front_matter and block.t == "Para" then
      local figure = figure_for_caption(text)
      if figure ~= nil then
        output:insert(figure_block(figure, figure_width(text)))
        output:insert(styled_block(block, "HFUTFigureCaption"))
      elseif text:match("^表[123]　") then
        output:insert(styled_block(block, "HFUTTableCaption"))
      else
        output:insert(styled_block(block, "HFUTBody"))
      end
    elseif block.t == "Div" and block.identifier == "refs" then
      output:insert(styled_text("参考文献", "HFUTReferenceHeading"))
      output:insert(block)
    else
      output:insert(block)
    end
  end

  doc.blocks = output
  return doc
end
