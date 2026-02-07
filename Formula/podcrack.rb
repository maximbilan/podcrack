class Podcrack < Formula
  desc "Apple Podcast Transcript Extractor"
  homepage "https://github.com/maximbilan/podcrack"
  url "https://github.com/maximbilan/podcrack/archive/refs/tags/v1.0.0.tar.gz"
  sha256 "f70aa6ac184187548113afc9389de88a33caffa13e67a6d549789a7ae352091a"
  license "MIT"
  head "https://github.com/maximbilan/podcrack.git", branch: "main"

  depends_on "python@3.10"

  def install
    python3 = Formula["python@3.10"].opt_bin/"python3.10"
    system python3, "-m", "pip", "install", "--upgrade", "pip", "setuptools", "wheel"
    system python3, "-m", "pip", "install", "--prefix=#{prefix}", "--no-warn-script-location", "."
  end

  test do
    # Verify the command exists and can be executed
    # podcrack is interactive, so we just check it runs
    output = shell_output("#{bin}/podcrack 2>&1", 1)
    assert_match "podcrack", output
  end
end
