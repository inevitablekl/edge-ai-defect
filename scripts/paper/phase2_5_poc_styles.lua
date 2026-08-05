-- Paper Phase 2.5 Step 6: TOOLCHAIN_POC_ONLY style bridge.
-- This filter injects synthetic full/anonymous front matter and maps source
-- semantics to named styles already present in the canonical reference DOCX.

local function meta_text(meta, key)
  local value = meta[key]
  if value == nil then
    return ""
  end
  return pandoc.utils.stringify(value)
end

local function styled(text, style)
  return pandoc.Div(
    {pandoc.Para(pandoc.Inlines{pandoc.Str(text)})},
    pandoc.Attr("", {}, {{"custom-style", style}})
  )
end

local function block_text(block)
  if block.t == "Para" or block.t == "Plain" then
    return pandoc.utils.stringify(block.content)
  end
  return ""
end

function Pandoc(doc)
  local identity_enabled = meta_text(doc.meta, "poc-identity-enabled") == "true"
  local output = pandoc.Blocks{}
  local body_started = false

  for _, block in ipairs(doc.blocks) do
    local text = block_text(block)

    if text == "POC_IDENTITY_BLOCK_MARKER" then
      if identity_enabled then
        output:insert(styled(meta_text(doc.meta, "poc-author-cn"), "HFUTAuthorsCN"))
        output:insert(styled(meta_text(doc.meta, "poc-affiliation-cn"), "HFUTAffiliationCN"))
        output:insert(styled(meta_text(doc.meta, "poc-author-en"), "HFUTAuthorsEN"))
        output:insert(styled(meta_text(doc.meta, "poc-affiliation-en"), "HFUTAffiliationEN"))
        output:insert(styled(meta_text(doc.meta, "poc-contact"), "HFUTBody"))
        output:insert(styled(meta_text(doc.meta, "poc-funding"), "HFUTFunding"))
        output:insert(styled(meta_text(doc.meta, "poc-biography"), "HFUTAuthorBiography"))
        output:insert(styled(meta_text(doc.meta, "poc-acknowledgement"), "HFUTAcknowledgement"))
      else
        output:insert(styled("ANONYMIZED_POC_CANDIDATE", "HFUTSpecimenNotice"))
        output:insert(styled("NOT_WORD_DOCUMENT_INSPECTOR_VERIFIED", "HFUTSpecimenNotice"))
      end
    elseif text == "BODY_SECTION_START_MARKER" then
      body_started = true
      output:insert(styled(text, "HFUTSpecimenNotice"))
    elseif block.t == "Header" then
      local style
      if block.identifier == "poc-introduction" then
        style = "HFUTIntroHeading"
      elseif block.level == 1 then
        style = "HFUTHeading1"
      elseif block.level == 2 then
        style = "HFUTHeading2"
      else
        style = "HFUTHeading3"
      end
      output:insert(pandoc.Div(
        {pandoc.Para(block.content)},
        pandoc.Attr(block.identifier, {}, {{"custom-style", style}})
      ))
    elseif body_started and block.t == "Para" then
      output:insert(pandoc.Div(
        {block},
        pandoc.Attr("", {}, {{"custom-style", "HFUTBody"}})
      ))
    else
      output:insert(block)
    end
  end

  doc.blocks = output
  return doc
end
