Add-Type -AssemblyName System.Drawing

$OutputPath = [System.IO.Path]::GetFullPath((Join-Path $PSScriptRoot '..\docs\social-preview\specforge-ai-social-preview.png'))
$DashboardPath = [System.IO.Path]::GetFullPath((Join-Path $PSScriptRoot '..\docs\screenshots\dashboard.png'))
[System.IO.Directory]::CreateDirectory([System.IO.Path]::GetDirectoryName($OutputPath)) | Out-Null

$Width = 1280
$Height = 640
$canvas = New-Object System.Drawing.Bitmap $Width, $Height
$graphics = [System.Drawing.Graphics]::FromImage($canvas)
$graphics.SmoothingMode = [System.Drawing.Drawing2D.SmoothingMode]::AntiAlias
$graphics.InterpolationMode = [System.Drawing.Drawing2D.InterpolationMode]::HighQualityBicubic
$graphics.PixelOffsetMode = [System.Drawing.Drawing2D.PixelOffsetMode]::HighQuality
$graphics.TextRenderingHint = [System.Drawing.Text.TextRenderingHint]::AntiAliasGridFit

function New-Color([string]$hex, [int]$alpha = 255) {
    $hex = $hex.TrimStart('#')
    $r = [Convert]::ToInt32($hex.Substring(0,2), 16)
    $g = [Convert]::ToInt32($hex.Substring(2,2), 16)
    $b = [Convert]::ToInt32($hex.Substring(4,2), 16)
    return [System.Drawing.Color]::FromArgb($alpha, $r, $g, $b)
}

function New-RoundedPath([System.Drawing.RectangleF]$rect, [float]$radius) {
    $path = New-Object System.Drawing.Drawing2D.GraphicsPath
    $diameter = $radius * 2
    $path.AddArc($rect.X, $rect.Y, $diameter, $diameter, 180, 90)
    $path.AddArc($rect.Right - $diameter, $rect.Y, $diameter, $diameter, 270, 90)
    $path.AddArc($rect.Right - $diameter, $rect.Bottom - $diameter, $diameter, $diameter, 0, 90)
    $path.AddArc($rect.X, $rect.Bottom - $diameter, $diameter, $diameter, 90, 90)
    $path.CloseFigure()
    return $path
}

function Draw-RoundedFill($g, [System.Drawing.Brush]$brush, [System.Drawing.RectangleF]$rect, [float]$radius) {
    $path = New-RoundedPath $rect $radius
    $g.FillPath($brush, $path)
    $path.Dispose()
}

function Draw-RoundedStroke($g, [System.Drawing.Pen]$pen, [System.Drawing.RectangleF]$rect, [float]$radius) {
    $path = New-RoundedPath $rect $radius
    $g.DrawPath($pen, $path)
    $path.Dispose()
}

function Draw-Pill($g, [string]$text, [float]$x, [float]$y, [string]$fillHex, [string]$textHex) {
    $font = New-Object System.Drawing.Font('Segoe UI Semibold', 16, [System.Drawing.FontStyle]::Regular)
    $paddingX = 18
    $paddingY = 10
    [System.Drawing.SizeF]$size = $g.MeasureString($text, $font)
    $width = [float]($size.Width + ($paddingX * 2))
    $height = [float]($size.Height + ($paddingY * 2) - 4)
    $rect = [System.Drawing.RectangleF]::new([float]$x, [float]$y, $width, $height)
    $brush = New-Object System.Drawing.SolidBrush (New-Color $fillHex)
    Draw-RoundedFill $g $brush $rect 18
    $brush.Dispose()
    $textBrush = New-Object System.Drawing.SolidBrush (New-Color $textHex)
    $g.DrawString($text, $font, $textBrush, [float]($x + $paddingX), [float]($y + $paddingY - 2))
    $textBrush.Dispose()
    $font.Dispose()
    return [float]($rect.Right + 12)
}

$background = New-Object System.Drawing.Drawing2D.LinearGradientBrush(
    ([System.Drawing.Point]::new(0,0)),
    ([System.Drawing.Point]::new($Width,$Height)),
    (New-Color '#FFF8EE'),
    (New-Color '#EEF4FF')
)
$graphics.FillRectangle($background, 0, 0, $Width, $Height)
$background.Dispose()

$shapeBrush1 = New-Object System.Drawing.SolidBrush (New-Color '#F4D7C8' 90)
$graphics.FillEllipse($shapeBrush1, 920, -60, 360, 260)
$shapeBrush1.Dispose()
$shapeBrush2 = New-Object System.Drawing.SolidBrush (New-Color '#E0ECFF' 120)
$graphics.FillEllipse($shapeBrush2, -120, 430, 340, 220)
$shapeBrush2.Dispose()
$shapeBrush3 = New-Object System.Drawing.SolidBrush (New-Color '#FFE7A8' 110)
$graphics.FillEllipse($shapeBrush3, 500, 520, 160, 120)
$shapeBrush3.Dispose()

$eyebrowBrush = New-Object System.Drawing.SolidBrush (New-Color '#1E293B')
$eyebrowFont = New-Object System.Drawing.Font('Segoe UI Semibold', 18, [System.Drawing.FontStyle]::Regular)
$graphics.DrawString('PORTFOLIO PROJECT', $eyebrowFont, $eyebrowBrush, 72, 64)
$eyebrowFont.Dispose()
$eyebrowBrush.Dispose()

$repoBrush = New-Object System.Drawing.SolidBrush (New-Color '#EA5B47')
$repoFont = New-Object System.Drawing.Font('Segoe UI Semibold', 20, [System.Drawing.FontStyle]::Regular)
$graphics.DrawString('yosuancrespo/specforge-ai', $repoFont, $repoBrush, 72, 94)
$repoFont.Dispose()
$repoBrush.Dispose()

$titleBrush = New-Object System.Drawing.SolidBrush (New-Color '#111827')
$titleFont = New-Object System.Drawing.Font('Bahnschrift', 58, [System.Drawing.FontStyle]::Bold)
$graphics.DrawString('SpecForge AI', $titleFont, $titleBrush, 68, 142)
$titleFont.Dispose()

$subtitleBrush = New-Object System.Drawing.SolidBrush (New-Color '#2B3A55')
$subtitleFont = New-Object System.Drawing.Font('Segoe UI Semibold', 27, [System.Drawing.FontStyle]::Regular)
$graphics.DrawString('AI-augmented QA platform', $subtitleFont, $subtitleBrush, 74, 234)
$subtitleFont.Dispose()

$bodyBrush = New-Object System.Drawing.SolidBrush (New-Color '#3F4C66')
$bodyFont = New-Object System.Drawing.Font('Segoe UI', 19, [System.Drawing.FontStyle]::Regular)
$bodyText = 'Spec-driven development and testing
RAG-grounded analysis, eval-driven
development and contract validation.'
$bodyRect = [System.Drawing.RectangleF]::new(74, 292, 520, 118)
$graphics.DrawString($bodyText, $bodyFont, $bodyBrush, $bodyRect)
$bodyFont.Dispose()
$bodyBrush.Dispose()

[float]$pillX = 74
[float]$pillY = 412
$pillX = Draw-Pill $graphics 'Python' $pillX $pillY '#1F3A8A' '#FFFFFF'
$pillX = Draw-Pill $graphics 'Go' $pillX $pillY '#0EA5E9' '#0F172A'
$pillX = Draw-Pill $graphics 'Rust' $pillX $pillY '#2B2B2B' '#FFFFFF'
$pillX = Draw-Pill $graphics 'Solidity' $pillX $pillY '#5B6170' '#FFFFFF'
[float]$pillX = 74
[float]$pillY = 470
$pillX = Draw-Pill $graphics 'FastAPI' $pillX $pillY '#DFF7EF' '#0F5132'
$pillX = Draw-Pill $graphics 'Streamlit' $pillX $pillY '#FFE4E0' '#7A1F1F'
$pillX = Draw-Pill $graphics 'pgvector' $pillX $pillY '#E2EEFF' '#123A7A'
$pillX = Draw-Pill $graphics 'promptfoo' $pillX $pillY '#FFF3D6' '#7C4A03'

$footerBrush = New-Object System.Drawing.SolidBrush (New-Color '#445067')
$footerFont = New-Object System.Drawing.Font('Segoe UI Semibold', 18, [System.Drawing.FontStyle]::Regular)
$graphics.DrawString('Hardhat | Foundry | n8n | Docker Compose | GitHub Actions', $footerFont, $footerBrush, 74, 548)
$footerFont.Dispose()
$footerBrush.Dispose()

$shadowRect = [System.Drawing.RectangleF]::new(650, 78, 560, 420)
$shadowBrush = New-Object System.Drawing.SolidBrush (New-Color '#101828' 24)
Draw-RoundedFill $graphics $shadowBrush $shadowRect 28
$shadowBrush.Dispose()

$panelRect = [System.Drawing.RectangleF]::new(636, 64, 560, 420)
$panelBrush = New-Object System.Drawing.SolidBrush (New-Color '#FFFFFF' 245)
Draw-RoundedFill $graphics $panelBrush $panelRect 28
$panelBrush.Dispose()
$panelPen = New-Object System.Drawing.Pen((New-Color '#D7DFEA'), 2)
Draw-RoundedStroke $graphics $panelPen $panelRect 28
$panelPen.Dispose()

$tagRect = [System.Drawing.RectangleF]::new(678, 90, 198, 38)
$tagBrush = New-Object System.Drawing.SolidBrush (New-Color '#111827')
Draw-RoundedFill $graphics $tagBrush $tagRect 18
$tagBrush.Dispose()
$tagTextBrush = New-Object System.Drawing.SolidBrush (New-Color '#FFFFFF')
$tagFont = New-Object System.Drawing.Font('Segoe UI Semibold', 16, [System.Drawing.FontStyle]::Regular)
$graphics.DrawString('LIVE DASHBOARD', $tagFont, $tagTextBrush, 698, 99)
$tagFont.Dispose()
$tagTextBrush.Dispose()

$dashboard = [System.Drawing.Image]::FromFile($DashboardPath)
$imageRect = [System.Drawing.RectangleF]::new(660, 138, 512, 300)
$clipPath = New-RoundedPath $imageRect 18
$state = $graphics.Save()
$graphics.SetClip($clipPath)
$tempBrush = New-Object System.Drawing.SolidBrush (New-Color '#F3F6FB')
$graphics.FillRectangle($tempBrush, $imageRect)
$tempBrush.Dispose()
$graphics.DrawImage($dashboard, [System.Drawing.Rectangle]::Round($imageRect))
$graphics.Restore($state)
$clipPath.Dispose()
$dashboard.Dispose()

$miniBrush = New-Object System.Drawing.SolidBrush (New-Color '#FFF8EE')
$miniRect = [System.Drawing.RectangleF]::new(680, 458, 476, 94)
Draw-RoundedFill $graphics $miniBrush $miniRect 18
$miniBrush.Dispose()
$miniPen = New-Object System.Drawing.Pen((New-Color '#F0D7C4'), 2)
Draw-RoundedStroke $graphics $miniPen $miniRect 18
$miniPen.Dispose()
$miniTitleBrush = New-Object System.Drawing.SolidBrush (New-Color '#111827')
$miniTitleFont = New-Object System.Drawing.Font('Segoe UI Semibold', 18, [System.Drawing.FontStyle]::Regular)
$graphics.DrawString('Validated end-to-end', $miniTitleFont, $miniTitleBrush, 702, 478)
$miniTitleFont.Dispose()
$miniBodyBrush = New-Object System.Drawing.SolidBrush (New-Color '#4B5563')
$miniBodyFont = New-Object System.Drawing.Font('Segoe UI', 14, [System.Drawing.FontStyle]::Regular)
$miniBodyRect = [System.Drawing.RectangleF]::new(702, 507, 430, 24)
$graphics.DrawString('CLI, API, dashboard and evals verified.', $miniBodyFont, $miniBodyBrush, $miniBodyRect)
$miniBodyFont.Dispose()
$miniBodyBrush.Dispose()
$miniTitleBrush.Dispose()
$titleBrush.Dispose()
$subtitleBrush.Dispose()

$canvas.Save($OutputPath, [System.Drawing.Imaging.ImageFormat]::Png)
$graphics.Dispose()
$canvas.Dispose()