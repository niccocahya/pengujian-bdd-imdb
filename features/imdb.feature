Feature: Pengujian fitur utama IMDB
  Scenario: User mencari film di IMDB
    Given pengguna membuka halaman utama IMDB
    When pengguna mencari film "The Secret Life of Walter Mitty"
    Then hasil pencarian menampilkan film yang berjudul "The Secret Life of Walter Mitty"

  Scenario: User membuka trailer film
    Given pengguna sudah berada di halaman hasil pencarian "The Secret Life of Walter Mitty"
    When pengguna mengklik film pertama
    And pengguna membuka tab trailer
    Then trailer film muncul di layar
